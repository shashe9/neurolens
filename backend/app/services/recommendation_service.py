import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.services.child_profile_service import build_child_profile
from app.knowledge.repository import (
    get_all_activities, get_all_guides, get_all_questions,
    ActivitySchema, GuideSchema, QuestionSchema
)

def score_activity(activity: ActivitySchema, profile: Dict[str, Any]) -> Dict[str, Any]:
    """Scores an activity against a child profile, and compiles the explanation."""
    score = 0
    reasons = []
    age = profile["age_months"]

    # 1. Age match
    if activity.age_min <= age <= activity.age_max:
        score += 50
        reasons.append("perfectly suited for their current age")
    elif activity.age_min - 3 <= age <= activity.age_max + 3:
        score += 20
        reasons.append("matches their immediate age band transition")

    # 2. Blind spot / Underrepresented domains
    blind_spot_match = False
    for d in activity.domains:
        if d.lower() in profile["underrepresented_domains"]:
            score += 40
            blind_spot_match = True
            reasons.append(f"helps build skills in the underrepresented {d.replace('_', ' ')} area")

    # 3. Focus themes / skills match
    theme_match = False
    for s in activity.skills:
        if s.lower() in profile["recent_focus_themes"] or s.lower() in [sig.lower() for sig in profile["growth_signals"]]:
            score += 30
            theme_match = True
            reasons.append(f"builds upon their recent focus on {s.replace('_', ' ')}")

    # 4. Concern matching
    concern_match = False
    for c in activity.related_concerns:
        if any(c.lower() in pc.lower() for pc in profile["persistent_concerns"]):
            score += 45
            concern_match = True
            reasons.append("helps address areas of recent caregiver concern")

    # Generate explanation
    if concern_match:
        why = f"Suggested to help monitor and support communication challenges or frustrations recently noted."
    elif theme_match:
        why = f"Recommended because your child recently showed focus or progress in {activity.skills[0].replace('_', ' ')}."
    elif blind_spot_match:
        why = f"Priced to help capture observations in {activity.domains[0].replace('_', ' ')}, where you have fewer entries lately."
    else:
        why = f"A developmentally supportive activity matching your child's age band of {age} months."

    # Build discrete personalization reasons:
    personalization_reasons = [f"Age: {age} months"]
    domain_counts = profile.get("domain_counts", {})
    for d in activity.domains:
        d_clean = d.lower().replace(" ", "_")
        cnt = domain_counts.get(d_clean, 0)
        d_display = d.replace("_", " ").capitalize()
        personalization_reasons.append(f"{d_display} observations: {cnt}")
        
    for s in activity.skills:
        s_clean = s.lower()
        if s_clean in [sig.lower() for sig in profile.get("growth_signals", [])]:
            personalization_reasons.append(f"Growth signal: '{s.replace('_', ' ').capitalize()}' detected")
        elif s_clean in profile.get("recent_focus_themes", []):
            personalization_reasons.append(f"Focus area: '{s.replace('_', ' ').capitalize()}'")
            
    for c in activity.related_concerns:
        for pc in profile.get("persistent_concerns", []):
            if c.lower() in pc.lower():
                personalization_reasons.append(f"Related concern: '{pc}'")
                break

    return {
        "activity": activity,
        "score": score,
        "why_recommended": why,
        "personalization_reasons": personalization_reasons
    }


def score_guide(guide: GuideSchema, profile: Dict[str, Any]) -> Dict[str, Any]:
    """Scores a guide against a child profile, and compiles the explanation."""
    score = 0
    reasons = []
    age = profile["age_months"]

    # 1. Age match
    if guide.age_min <= age <= guide.age_max:
        score += 50
        reasons.append("age-relevant guidance")
    elif guide.age_min - 3 <= age <= guide.age_max + 3:
        score += 20

    # 2. Domain match (Blind spots)
    for d in guide.domains:
        if d.lower() in profile["underrepresented_domains"]:
            score += 35
            reasons.append(f"covers the blind spot domain {d.replace('_', ' ')}")

    # 3. Concern match
    concern_match = False
    for c in guide.related_concerns:
        if any(c.lower() in pc.lower() for pc in profile["persistent_concerns"]):
            score += 45
            concern_match = True

    # Generate explanation
    if concern_match:
        why = "Recommended reading to help navigate and support recent concern topics."
    elif len(profile["underrepresented_domains"]) > 0 and guide.domains[0].lower() in profile["underrepresented_domains"]:
        why = f"Insightful guide covering {guide.domains[0].replace('_', ' ')}: an area with low logging coverage recently."
    else:
        why = f"A quick educational guide for parents of children in the {age} month age range."

    # Build discrete personalization reasons:
    personalization_reasons = [f"Age: {age} months"]
    domain_counts = profile.get("domain_counts", {})
    for d in guide.domains:
        d_clean = d.lower().replace(" ", "_")
        cnt = domain_counts.get(d_clean, 0)
        d_display = d.replace("_", " ").capitalize()
        personalization_reasons.append(f"{d_display} observations: {cnt}")
        
    for s in guide.skills:
        s_clean = s.lower()
        if s_clean in [sig.lower() for sig in profile.get("growth_signals", [])]:
            personalization_reasons.append(f"Growth signal: '{s.replace('_', ' ').capitalize()}' detected")
        elif s_clean in profile.get("recent_focus_themes", []):
            personalization_reasons.append(f"Focus area: '{s.replace('_', ' ').capitalize()}'")
            
    for c in guide.related_concerns:
        for pc in profile.get("persistent_concerns", []):
            if c.lower() in pc.lower():
                personalization_reasons.append(f"Related concern: '{pc}'")
                break

    return {
        "guide": guide,
        "score": score,
        "why_recommended": why,
        "personalization_reasons": personalization_reasons
    }


def score_question(q: QuestionSchema, profile: Dict[str, Any]) -> Dict[str, Any]:
    """Scores a question against a child profile, and compiles the explanation."""
    score = 0
    age = profile["age_months"]

    # 1. Age match
    if q.age_min <= age <= q.age_max:
        score += 50

    # 2. Domain match (Blind spots)
    for d in q.domains:
        if d.lower() in profile["underrepresented_domains"]:
            score += 30

    # 3. Priority check
    score += q.priority * 10

    return {
        "question": q,
        "score": score
    }


def get_personalized_recommendations(db: Session, child_id: uuid.UUID) -> Dict[str, Any]:
    """Compiles scored and ranked activities, guides, and questions based on real data."""
    # 1. Build child profile vector
    profile = build_child_profile(db, child_id)

    # 2. Load knowledge base
    all_activities = get_all_activities()
    all_guides = get_all_guides()
    all_questions = get_all_questions()

    # 3. Score activities
    scored_activities = [score_activity(act, profile) for act in all_activities]

    # 4. Score guides
    scored_guides = [score_guide(gd, profile) for gd in all_guides]

    # 5. Re-rank using parent behavior feedback metrics (ratios)
    from app.services.recommendation_ranking_service import rank_recommendations
    ranked = rank_recommendations(db, child_id, scored_activities, scored_guides)
    scored_activities = ranked["activities"]
    scored_guides = ranked["guides"]

    # 6. Score and sort questions
    scored_questions = [score_question(q, profile) for q in all_questions]
    scored_questions.sort(key=lambda x: x["score"], reverse=True)

    # Pick top suggestions
    rec_activities = []
    for item in scored_activities[:2]:
        act = item["activity"]
        rec_activities.append({
            "id": act.id,
            "title": act.title,
            "summary": act.summary,
            "duration_minutes": act.duration_minutes,
            "materials": act.materials,
            "instructions": act.instructions,
            "why_recommended": item["why_recommended"],
            "personalization_reasons": item.get("personalization_reasons", [])
        })

    rec_guides = []
    for item in scored_guides[:2]:
        gd = item["guide"]
        rec_guides.append({
            "id": gd.id,
            "title": gd.title,
            "summary": gd.summary,
            "reading_time": gd.reading_time,
            "body_markdown": gd.body_markdown,
            "why_recommended": item["why_recommended"],
            "personalization_reasons": item.get("personalization_reasons", [])
        })

    # Pull top question
    rec_question = None
    if scored_questions:
        q_obj = scored_questions[0]["question"]
        rec_question = {
            "id": q_obj.id,
            "question": q_obj.question,
            "follow_up_prompt": q_obj.follow_up_prompt
        }

    # Timeline targets
    next_observations = profile["recommended_targets"]

    return {
        "child_profile": profile,
        "activities": rec_activities,
        "guides": rec_guides,
        "question": rec_question,
        "next_observations": next_observations
    }
