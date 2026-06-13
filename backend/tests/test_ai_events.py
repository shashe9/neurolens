import uuid
from datetime import datetime
from app.models.models import (
    Parent,
    Child,
    Observation,
    ObservationType,
    AISuggestionEvent,
    Milestone,
    DevelopmentalDomain,
    InteractionType
)

def test_ai_suggestion_event_persistence(db):
    # 1. Create Parent & Child
    parent = Parent(first_name="Test", last_name="Parent", email="ai.test.parent@example.com")
    db.add(parent)
    db.commit()
    db.refresh(parent)

    child = Child(first_name="Test", last_name="Child", date_of_birth=datetime(2024, 6, 15).date(), gender="Male")
    db.add(child)
    db.commit()
    db.refresh(child)

    # 2. Create Domain & Observation
    domain = DevelopmentalDomain(name="Test Domain", description="Testing OIE domain linkage")
    db.add(domain)
    db.commit()
    db.refresh(domain)

    observation = Observation(
        child_id=child.id,
        parent_id=parent.id,
        body="Child pointed to the apple on the table.",
        entry_type=ObservationType.GENERAL,
        domain_id=domain.id,
        observed_at=datetime.utcnow()
    )
    db.add(observation)
    db.commit()
    db.refresh(observation)

    # 3. Create Milestone
    milestone = Milestone(
        domain_id=domain.id,
        title="Points to show someone what he wants",
        description="Points to object to draw attention",
        age_range_low=18,
        age_range_high=24
    )
    db.add(milestone)
    db.commit()
    db.refresh(milestone)

    # 4. Create AI Suggestion Event
    event = AISuggestionEvent(
        child_id=child.id,
        observation_id=observation.id,
        raw_text="Child pointed to the apple on the table.",
        suggested_domains=[{"name": "Test Domain", "score": 0.85}],
        suggested_milestones=[{"id": str(milestone.id), "score": 0.91}],
        selected_domain="Test Domain",
        selected_milestone_id=milestone.id,
        max_similarity=0.91,
        relevance_rank="STRONG",
        interaction_type=InteractionType.ACCEPTED,
        model_version="oie_v1_multilingual",
        processing_time_ms=25,
        created_at=datetime.utcnow(),
        accepted_at=datetime.utcnow()
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # 5. Verify fields have persisted correctly
    assert event.id is not None
    assert event.child_id == child.id
    assert event.observation_id == observation.id
    assert event.selected_milestone_id == milestone.id
    assert event.max_similarity == 0.91
    assert event.relevance_rank == "STRONG"
    assert event.interaction_type == InteractionType.ACCEPTED
    assert event.model_version == "oie_v1_multilingual"
    assert event.processing_time_ms == 25

    # 6. Verify Relationships
    # Child -> AI Events
    assert len(child.ai_suggestion_events) == 1
    assert child.ai_suggestion_events[0].id == event.id

    # Observation -> AI Events
    assert len(observation.ai_suggestion_events) == 1
    assert observation.ai_suggestion_events[0].id == event.id

    # Milestone -> AI Events
    assert len(milestone.ai_suggestion_events) == 1
    assert milestone.ai_suggestion_events[0].id == event.id

    # 7. Test Update
    event.interaction_type = InteractionType.OVERRIDDEN
    event.error_type = "none"
    db.commit()
    db.refresh(event)

    assert event.interaction_type == InteractionType.OVERRIDDEN
    assert event.error_type == "none"

    # 8. Test foreign key nullification on delete observation (SET NULL constraint)
    db.delete(observation)
    db.commit()
    db.refresh(event)

    # Foreign key should automatically set to null due to SET NULL behavior
    assert event.observation_id is None
