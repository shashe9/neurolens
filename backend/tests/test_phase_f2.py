import pytest
import uuid
from datetime import datetime, date, timedelta
from app.models.models import Parent, Child, Observation, ObservationType, DevelopmentalDomain
from app.services.observation_quality_service import calculate_single_observation_quality
from app.services.recommendation_ranking_service import calculate_parent_preference_metrics, rank_recommendations
from app.services.learning_path_service import generate_personalized_learning_path
from app.services.companion_timeline_service import get_companion_timeline
from app.models.models import RecommendationFeedback, ActivityOutcome, parent_child_links, ClinicalVisit

def test_observation_quality_scoring():
    # Test short, vague log
    score_low = calculate_single_observation_quality("He looked happy")
    assert score_low < 0.3

    # Test rich log with context and specific keywords
    score_high = calculate_single_observation_quality(
        body="Responded to name 8 of 10 times during dinner at the kitchen table.",
        location="Kitchen",
        observer_relation="Mother",
        context_note="Structured name-response test"
    )
    assert score_high >= 0.7
    assert score_high <= 1.0

def test_concern_evolution_confidence_endpoint(client, db):
    parent = db.query(Parent).order_by(Parent.created_at.desc()).first()
    if not parent:
        parent = Parent(first_name="P", last_name="P", email="p@example.com")
        db.add(parent)
        db.commit()

    child = Child(
        first_name="F2Child",
        last_name="Test",
        date_of_birth=date.today() - timedelta(days=600),
        gender="Male"
    )
    db.add(child)
    db.commit()

    db.execute(
        parent_child_links.insert().values(
            parent_id=parent.id,
            child_id=child.id,
            relationship_type="parent"
        )
    )
    db.commit()

    domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.name == "Communication").first()
    if not domain:
        domain = DevelopmentalDomain(name="Communication", description="Speech")
        db.add(domain)
        db.commit()

    # 1. Low Confidence: Under 2 logs in the last 30 days
    response = client.get(f"/insights/{child.id}/concern-evolution")
    assert response.status_code == 200
    res_json = response.json()
    assert len(res_json["evolution"]) == 0 # no concerns logged yet

    # Log 1 concern
    obs1 = Observation(
        child_id=child.id,
        parent_id=parent.id,
        body="Does not make eye contact when called",
        entry_type=ObservationType.CONCERN,
        domain_id=domain.id,
        observed_at=datetime.utcnow() - timedelta(days=5),
        quality_score=0.8
    )
    db.add(obs1)
    db.commit()

    response = client.get(f"/insights/{child.id}/concern-evolution")
    res_json = response.json()
    assert len(res_json["evolution"]) == 1
    assert res_json["evolution"][0]["confidence"] == "Low"
    assert "Insufficient recent observations" in res_json["evolution"][0]["reason"]

    # Log 2 more concerns to reach Medium confidence (3 total)
    obs2 = Observation(
        child_id=child.id,
        parent_id=parent.id,
        body="Does not respond to name 2 out of 5 times",
        entry_type=ObservationType.CONCERN,
        domain_id=domain.id,
        observed_at=datetime.utcnow() - timedelta(days=2),
        quality_score=0.9
    )
    obs3 = Observation(
        child_id=child.id,
        parent_id=parent.id,
        body="Fails to check parents face",
        entry_type=ObservationType.CONCERN,
        domain_id=domain.id,
        observed_at=datetime.utcnow() - timedelta(days=1),
        quality_score=0.7
    )
    db.add(obs2)
    db.add(obs3)
    db.commit()

    response = client.get(f"/insights/{child.id}/concern-evolution")
    res_json = response.json()
    assert res_json["evolution"][0]["confidence"] == "Medium"

def test_dynamic_ranking_and_feedback(client, db):
    parent = db.query(Parent).order_by(Parent.created_at.desc()).first()
    child = Child(
        first_name="FeedbackChild",
        last_name="Test",
        date_of_birth=date.today() - timedelta(days=600),
        gender="Male"
    )
    db.add(child)
    db.commit()

    db.execute(
        parent_child_links.insert().values(
            parent_id=parent.id,
            child_id=child.id,
            relationship_type="parent"
        )
    )
    db.commit()

    # Log recommendation feedback
    fb1 = RecommendationFeedback(
        child_id=child.id,
        recommendation_id="GD_001",
        recommendation_type="guide",
        opened_at=datetime.utcnow(),
        completed=True
    )
    fb2 = RecommendationFeedback(
        child_id=child.id,
        recommendation_id="ACT_001",
        recommendation_type="activity",
        opened_at=datetime.utcnow(),
        completed=False
    )
    db.add(fb1)
    db.add(fb2)
    db.commit()

    # Calculate metrics
    metrics = calculate_parent_preference_metrics(db, child.id)
    assert metrics["guide_completion_rate"] == 1.0
    assert metrics["activity_completion_rate"] == 0.0

    # Test POST activity-outcomes
    response = client.post(
        "/recommendations/activity-outcomes",
        json={
            "child_id": str(child.id),
            "activity_id": "ACT_001",
            "attempted": True,
            "completed": True,
            "parent_notes": "Very successful",
            "observed_change": "More eye contact afterward"
        }
    )
    assert response.status_code == 201
    
    # Verify outcome exists in database
    outcome = db.query(ActivityOutcome).filter(ActivityOutcome.child_id == child.id).first()
    assert outcome is not None
    assert outcome.completed is True

def test_companion_timeline_and_learning_path(client, db):
    parent = db.query(Parent).order_by(Parent.created_at.desc()).first()
    child = Child(
        first_name="PathChild",
        last_name="Test",
        date_of_birth=date.today() - timedelta(days=600),
        gender="Male"
    )
    db.add(child)
    db.commit()

    db.execute(
        parent_child_links.insert().values(
            parent_id=parent.id,
            child_id=child.id,
            relationship_type="parent"
        )
    )
    db.commit()

    # Add clinical visit
    visit = ClinicalVisit(
        child_id=child.id,
        visit_date=date.today() - timedelta(days=10),
        clinician_name="Dr. Smith",
        visit_priority="routine",
        concern_level="low",
        concern_note="Initial assessment"
    )
    db.add(visit)
    db.commit()

    # Verify timeline is populated
    timeline = get_companion_timeline(db, child.id)
    assert len(timeline) >= 1
    assert timeline[0]["type"] == "visit"
    assert timeline[0]["metadata"]["clinician_name"] == "Dr. Smith"

    # Verify learning path API works
    response = client.get(f"/insights/{child.id}/learning-path")
    assert response.status_code == 200
    res_json = response.json()
    assert "target_skill" in res_json
    assert "weeks" in res_json
    assert len(res_json["weeks"]) == 4
