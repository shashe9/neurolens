import pytest
import uuid
from datetime import datetime, date, timedelta
from app.models.models import Parent, Child, Observation, ObservationType, DevelopmentalDomain, Milestone, MilestoneStatus
from app.knowledge.repository import get_all_activities, get_all_guides, get_all_questions
from app.services.child_profile_service import build_child_profile
from app.services.recommendation_service import get_personalized_recommendations

def test_repository_loading():
    activities = get_all_activities()
    guides = get_all_guides()
    questions = get_all_questions()

    assert len(activities) > 0
    assert len(guides) > 0
    assert len(questions) > 0

    assert activities[0].id is not None
    assert guides[0].title is not None
    assert questions[0].question is not None

def test_recommendation_logic(db):
    # Setup parent and child
    parent = Parent(
        first_name="Recommend",
        last_name="Parent",
        email="recommend.parent@example.com"
    )
    db.add(parent)
    db.commit()
    db.refresh(parent)

    child = Child(
        first_name="Alice",
        last_name="Wonderland",
        date_of_birth=date.today() - timedelta(days=540), # 18 months old
        gender="Female"
    )
    db.add(child)
    db.commit()
    db.refresh(child)

    # Link
    from app.models.models import parent_child_links
    db.execute(
        parent_child_links.insert().values(
            parent_id=parent.id,
            child_id=child.id,
            relationship_type="parent"
        )
    )
    db.commit()

    # Add communication domain and observation
    comm_domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.name == "Communication").first()
    if not comm_domain:
        comm_domain = DevelopmentalDomain(name="Communication", description="Speech")
        db.add(comm_domain)
        db.commit()
        db.refresh(comm_domain)

    obs = Observation(
        child_id=child.id,
        parent_id=parent.id,
        body="Alice was pointing and showing a toy to share interest today.",
        entry_type=ObservationType.GENERAL,
        domain_id=comm_domain.id,
        observed_at=datetime.utcnow()
    )
    db.add(obs)
    db.commit()

    # Generate profile
    profile = build_child_profile(db, child.id)
    assert profile["age_months"] == 18
    assert "pointing_gesture" in profile["growth_signals"]

    # Generate recommendations
    recs = get_personalized_recommendations(db, child.id)
    assert "activities" in recs
    assert "guides" in recs
    assert len(recs["activities"]) > 0
    assert len(recs["guides"]) > 0
    assert recs["activities"][0]["why_recommended"] is not None

def test_recommendation_api_endpoint(client, db):
    # Retrieve the last parent or create one
    parent = db.query(Parent).order_by(Parent.created_at.desc()).first()
    if not parent:
        parent = Parent(
            first_name="API",
            last_name="Parent",
            email="api.parent@example.com"
        )
        db.add(parent)
        db.commit()
        db.refresh(parent)

    child = Child(
        first_name="Bobby",
        last_name="Tables",
        date_of_birth=date.today() - timedelta(days=540),
        gender="Male"
    )
    db.add(child)
    db.commit()
    db.refresh(child)

    from app.models.models import parent_child_links
    db.execute(
        parent_child_links.insert().values(
            parent_id=parent.id,
            child_id=child.id,
            relationship_type="parent"
        )
    )
    db.commit()

    # Call recommendation API
    response = client.get(f"/insights/{child.id}/recommendations")
    assert response.status_code == 200
    res_json = response.json()
    assert "activities" in res_json
    assert "guides" in res_json
    assert "question" in res_json
    assert "child_profile" in res_json
    assert len(res_json["activities"]) > 0
