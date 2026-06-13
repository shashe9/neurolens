import uuid
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import Counter
import numpy as np

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import Child, Milestone, AISuggestionEvent, InteractionType, Parent, parent_child_links
from app.api.dependencies import get_current_parent
from app.schemas.schemas import (
    AISuggestRequest,
    AISuggestResponse,
    AIConfirmRequest,
    DomainSuggestion,
    ObservationSuggestion
)
from app.services.ai_service import ai_engine
from app.services.pattern_service import ObservationPatternExtractor

router = APIRouter()

@router.post("/suggest", response_model=AISuggestResponse, status_code=status.HTTP_200_OK)
def suggest_milestones(
    request: AISuggestRequest, 
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    start_time = time.perf_counter()

    # 1. Validate child profile exists
    child = db.query(Child).filter(Child.id == request.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )

    # Check parent-child link ownership
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == request.child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have access to this child profile."
        )

    # Make sure AI engine milestone cache is initialized
    if len(ai_engine.milestone_ids) == 0:
        try:
            ai_engine.initialize_cache(db)
        except RuntimeError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    try:
        # 2. Run pattern extraction
        patterns, explanation_cues, report_keywords = ObservationPatternExtractor.extract(request.observation_text)

        # 3. Preprocess and compute observation embedding
        preprocessed_text = ai_engine.preprocess_text(request.observation_text)
        obs_vector = ai_engine.model.encode(preprocessed_text, convert_to_numpy=True)
        obs_norm = np.linalg.norm(obs_vector)
        if obs_norm > 0:
            obs_vector /= obs_norm

        # 4. Run milestone and domain retrieval
        suggested_milestones_raw = ai_engine.retrieve_milestones(obs_vector, request.child_age_months)
        suggested_domains_raw = ai_engine.retrieve_domains(obs_vector, request.child_age_months)

        # Map to Pydantic responses
        domains = [
            DomainSuggestion(
                domain_name=d["domain_name"],
                relevance_score=d["relevance_score"],
                relevance_label=d["relevance_label"]
            )
            for d in suggested_domains_raw
        ]

        import re

        # Parse translated Hinglish terms from input text
        words = re.findall(r"\b\w+\b", request.observation_text.lower())
        translated_terms_all = []
        seen_raw = set()
        for w in words:
            if w in ai_engine.transliteration_glossary and w not in seen_raw:
                seen_raw.add(w)
                translated_terms_all.append({
                    "raw": w,
                    "translated": ai_engine.transliteration_glossary[w]
                })

        milestones = []
        for m in suggested_milestones_raw:
            m_id = m["milestone_id"]
            meta = ai_engine.milestone_metadata[m_id]
            domain_name = meta["domain_name"]
            age_low = meta["age_range_low"]
            age_high = meta["age_range_high"]
            age = request.child_age_months

            # Determine age suitability
            if age_low <= age <= age_high:
                age_band_relevance = f"Within typical range ({age_low}-{age_high} months)"
                age_explanation = f"Child is {age} months, which matches the typical age range of {age_low}-{age_high} months."
            elif age > age_high:
                age_band_relevance = f"Developmental screening suitability (typical limit: {age_high} months)"
                age_explanation = f"Child is {age} months. This milestone is typically achieved by {age_high} months, helping screen for delays."
            else:
                age_band_relevance = f"Emerging skill tracking (typical start: {age_low} months)"
                age_explanation = f"Child is {age} months. This milestone is typically expected later at {age_low}-{age_high} months."

            # Construct final explanation text
            explanation_text = (
                f"This milestone was retrieved based on semantic similarity to behavioral patterns in the {domain_name} domain. "
                f"{age_explanation}"
            )
            if translated_terms_all:
                terms_str = ", ".join([f"'{t['raw']}' ({t['translated']})" for t in translated_terms_all])
                explanation_text += f" Caregiver terminology matched: {terms_str}."

            milestones.append(
                ObservationSuggestion(
                    milestone_id=m["milestone_id"],
                    title=m["title"],
                    relevance_score=m["relevance_score"],
                    relevance_label=m["relevance_label"],
                    translated_terms=translated_terms_all,
                    domain_name=domain_name,
                    age_band_relevance=age_band_relevance,
                    explanation_text=explanation_text
                )
            )

        # 5. Generate explanations (combine pattern matches, similarity evidence, and overlap)
        explanations = [m.explanation_text for m in milestones]

        # Calculate max similarity and relevance rank
        max_similarity = 0.0
        relevance_rank = "no_strong_match"
        if milestones:
            max_similarity = milestones[0].relevance_score
            relevance_rank = milestones[0].relevance_label

        processing_time_ms = int((time.perf_counter() - start_time) * 1000)

        # 6. Create AISuggestionEvent
        db_event = AISuggestionEvent(
            child_id=request.child_id,
            observation_id=None,  # Not linked to a saved observation yet
            raw_text=request.observation_text,
            suggested_domains=[d.model_dump() for d in domains],
            suggested_milestones=[{**m.model_dump(), "milestone_id": str(m.milestone_id)} for m in milestones],
            selected_domain=None,
            selected_milestone_id=None,
            max_similarity=max_similarity,
            relevance_rank=relevance_rank,
            interaction_type=InteractionType.IGNORED,
            model_version=ai_engine.model_version,
            processing_time_ms=processing_time_ms,
            created_at=datetime.utcnow()
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)

        return AISuggestResponse(
            domains=domains,
            milestones=milestones,
            observation_patterns=patterns,
            report_keywords=report_keywords,
            explanations=explanations,
            event_id=db_event.id,
            model_version=db_event.model_version
        )


    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI suggestion processing failed: {str(e)}"
        )


@router.post("/confirm/{event_id}", status_code=status.HTTP_200_OK)
def confirm_suggestion(
    event_id: uuid.UUID, 
    request: AIConfirmRequest, 
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    event = db.query(AISuggestionEvent).filter(AISuggestionEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI suggestion event not found."
        )

    # Check parent-child link ownership
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == event.child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have access to this recommendation."
        )

    # Validate milestone_id if provided
    if request.selected_milestone_id:
        milestone = db.query(Milestone).filter(Milestone.id == request.selected_milestone_id).first()
        if not milestone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected milestone does not exist."
            )

    try:
        event.interaction_type = request.interaction_type
        event.selected_domain = request.selected_domain
        event.selected_milestone_id = request.selected_milestone_id
        if request.interaction_type == InteractionType.ACCEPTED:
            event.accepted_at = datetime.utcnow()
        else:
            event.accepted_at = None

        db.commit()
        db.refresh(event)
        return {
            "id": event.id,
            "child_id": event.child_id,
            "observation_id": event.observation_id,
            "raw_text": event.raw_text,
            "selected_domain": event.selected_domain,
            "selected_milestone_id": event.selected_milestone_id,
            "interaction_type": event.interaction_type,
            "model_version": event.model_version,
            "accepted_at": event.accepted_at,
            "created_at": event.created_at
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to confirm suggestion: {str(e)}"
        )


@router.get("/events/{child_id}", status_code=status.HTTP_200_OK)
def get_ai_events(
    child_id: uuid.UUID, 
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # Validate child profile exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )

    # Check parent-child link ownership
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have access to this child profile."
        )

    events = db.query(AISuggestionEvent).filter(
        AISuggestionEvent.child_id == child_id
    ).order_by(AISuggestionEvent.created_at.desc()).all()

    return [
        {
            "id": e.id,
            "child_id": e.child_id,
            "observation_id": e.observation_id,
            "raw_text": e.raw_text,
            "suggested_domains": e.suggested_domains,
            "suggested_milestones": e.suggested_milestones,
            "selected_domain": e.selected_domain,
            "selected_milestone_id": e.selected_milestone_id,
            "max_similarity": e.max_similarity,
            "relevance_rank": e.relevance_rank,
            "interaction_type": e.interaction_type,
            "model_version": e.model_version,
            "processing_time_ms": e.processing_time_ms,
            "created_at": e.created_at,
            "accepted_at": e.accepted_at
        }
        for e in events
    ]


@router.get("/metrics/{child_id}", status_code=status.HTTP_200_OK)
def get_ai_metrics(
    child_id: uuid.UUID, 
    db: Session = Depends(get_db),
    current_parent: Parent = Depends(get_current_parent)
):
    # Validate child profile exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found."
        )

    # Check parent-child link ownership
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == current_parent.id,
            parent_child_links.c.child_id == child_id
        )
    ).first()
    if not is_linked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have access to this child profile."
        )

    events = db.query(AISuggestionEvent).filter(
        AISuggestionEvent.child_id == child_id
    ).all()

    total_suggestions = len(events)
    accepted = sum(1 for e in events if e.interaction_type == InteractionType.ACCEPTED)
    overridden = sum(1 for e in events if e.interaction_type == InteractionType.OVERRIDDEN)
    ignored = sum(1 for e in events if e.interaction_type == InteractionType.IGNORED)
    manual_only = sum(1 for e in events if e.interaction_type == InteractionType.MANUAL_ONLY)

    acceptance_rate = float(accepted) / total_suggestions if total_suggestions > 0 else 0.0

    # Count top domains (from accepted suggestion events)
    accepted_domains = [e.selected_domain for e in events if e.selected_domain and e.interaction_type == InteractionType.ACCEPTED]
    domain_counts = Counter(accepted_domains)
    top_domains = [domain for domain, _ in domain_counts.most_common(5)]

    # Count top milestones (from accepted suggestion events)
    accepted_milestone_ids = [e.selected_milestone_id for e in events if e.selected_milestone_id and e.interaction_type == InteractionType.ACCEPTED]
    top_milestones = []
    if accepted_milestone_ids:
        milestone_counts = Counter(accepted_milestone_ids)
        top_milestone_tuples = milestone_counts.most_common(5)
        for m_id, _ in top_milestone_tuples:
            m = db.query(Milestone).filter(Milestone.id == m_id).first()
            if m:
                top_milestones.append(m.title)

    return {
        "total_suggestions": total_suggestions,
        "accepted": accepted,
        "overridden": overridden,
        "ignored": ignored,
        "manual_only": manual_only,
        "acceptance_rate": round(acceptance_rate, 4),
        "top_domains": top_domains,
        "top_milestones": top_milestones
    }
