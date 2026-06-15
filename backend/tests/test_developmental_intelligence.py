import pytest
import uuid
from datetime import datetime, date, timedelta
from app.models.models import Parent, Child, Observation, ObservationType, DevelopmentalDomain, Milestone, MilestoneStatus, First
from app.schemas.schemas import SnapshotResponse, GrowthStoryResponse, FirstResponse

def test_developmental_intelligence_logic(db):
    # 1. Create a parent and child
    parent = Parent(
        first_name="Story",
        last_name="Parent",
        email="story.parent@example.com"
    )
    db.add(parent)
    db.commit()
    db.refresh(parent)

    child = Child(
        first_name="Baby",
        last_name="Einstein",
        date_of_birth=date.today() - timedelta(days=690), # 23 months old
        gender="Female"
    )
    db.add(child)
    db.commit()
    db.refresh(child)

    # Link child to parent
    from app.models.models import parent_child_links
    db.execute(
        parent_child_links.insert().values(
            parent_id=parent.id,
            child_id=child.id,
            relationship_type="parent"
        )
    )
    db.commit()

    # Retrieve domains
    comm_domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.name == "Communication").first()
    if not comm_domain:
        comm_domain = DevelopmentalDomain(name="Communication", description="Speech & expression")
        db.add(comm_domain)
        db.commit()
        db.refresh(comm_domain)

    # 2. Add observations for this month and previous month
    now = datetime.utcnow()
    # This month (current month)
    obs1 = Observation(
        child_id=child.id,
        parent_id=parent.id,
        body="Baby said her first word today! Also pointed to a cat.",
        entry_type=ObservationType.GENERAL,
        domain_id=comm_domain.id,
        observed_at=now
    )
    # Previous month (35 days ago)
    obs_prev = Observation(
        child_id=child.id,
        parent_id=parent.id,
        body="Struggling to communicate what she wants and getting frustrated.",
        entry_type=ObservationType.CONCERN,
        domain_id=comm_domain.id,
        observed_at=now - timedelta(days=35)
    )
    db.add_all([obs1, obs_prev])
    db.commit()

    # 3. Test generate_monthly_snapshot
    from app.services.developmental_intelligence_service import generate_monthly_snapshot
    current_month_str = now.strftime("%Y-%m")
    snapshot = generate_monthly_snapshot(db, child.id, current_month_str)

    assert snapshot["month"] == current_month_str
    assert snapshot["observation_count"] == 1
    assert snapshot["domains"]["communication"] == 1
    assert len(snapshot["active_themes"]) > 0

    # 4. Test generate_child_snapshot
    from app.services.developmental_intelligence_service import generate_child_snapshot
    child_snapshot = generate_child_snapshot(db, child.id)
    assert child_snapshot["child_name"] == "Baby Einstein"
    assert child_snapshot["age_months"] == 23
    assert child_snapshot["most_observed_area"] == "Communication"

    # 5. Test generate_growth_story
    from app.services.developmental_intelligence_service import generate_growth_story
    growth_story = generate_growth_story(db, child.id, current_month_str)
    assert "Baby" in growth_story["title"]
    assert len(growth_story["story"]) > 0
    assert "In June" in growth_story["story"] or f"In {now.strftime('%B')}" in growth_story["story"]

    # 6. Test generate_monthly_change_summary
    from app.services.developmental_intelligence_service import generate_monthly_change_summary
    changes = generate_monthly_change_summary(db, child.id, current_month_str)
    assert len(changes) > 0

    # 7. Test generate_monthly_questions
    from app.services.developmental_intelligence_service import generate_monthly_questions
    questions = generate_monthly_questions(db, child.id)
    assert len(questions) >= 3


def test_developmental_intelligence_endpoints(client, db):
    # 1. Retrieve the parent and create a child profile
    parent = db.query(Parent).order_by(Parent.created_at.desc()).first()
    child = Child(
        first_name="Rohan",
        last_name="Sharma",
        date_of_birth=date.today() - timedelta(days=700), # 23 months old
        gender="Male"
    )
    db.add(child)
    db.commit()
    db.refresh(child)

    # Link parent and child via mapping
    from app.models.models import parent_child_links
    db.execute(
        parent_child_links.insert().values(
            parent_id=parent.id,
            child_id=child.id,
            relationship_type="parent"
        )
    )
    db.commit()

    # Create observation to populate data
    comm_domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.name == "Communication").first()
    obs = Observation(
        child_id=child.id,
        parent_id=parent.id,
        body="Rohan said first word today!",
        entry_type=ObservationType.GENERAL,
        domain_id=comm_domain.id if comm_domain else None,
        observed_at=datetime.utcnow()
    )
    db.add(obs)
    db.commit()

    # A. Test snapshot GET
    response = client.get(f"/insights/{child.id}/snapshot")
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["child_name"] == "Rohan Sharma"
    assert res_json["age_months"] == 23

    # B. Test growth-story GET
    response = client.get(f"/insights/{child.id}/growth-story")
    assert response.status_code == 200
    res_json = response.json()
    assert "Rohan" in res_json["title"]
    assert "story" in res_json

    # C. Test monthly-change GET
    response = client.get(f"/insights/{child.id}/monthly-change")
    assert response.status_code == 200
    res_json = response.json()
    assert isinstance(res_json, list)

    # D. Test monthly-questions GET
    response = client.get(f"/insights/{child.id}/monthly-questions")
    assert response.status_code == 200
    res_json = response.json()
    assert isinstance(res_json, list)
    assert len(res_json) >= 3

    # E. Test First candidate detection on observation creation
    obs_payload = {
        "parent_id": str(parent.id),
        "body": "We saw Rohan point for the first time pointing at a ball today!",
        "entry_type": "general",
        "domain_id": comm_domain.id if comm_domain else None
    }
    response = client.post(f"/children/{child.id}/observations", json=obs_payload)
    assert response.status_code == 201
    res_json = response.json()
    assert res_json["first_suggestion"] == "First Pointing Moment"

    # F. Test Firsts confirmed list is empty initially
    response = client.get(f"/insights/{child.id}/firsts")
    assert response.status_code == 200
    assert len(response.json()) == 0

    # G. Test First POST (Save confirmed first)
    first_payload = {
        "first_title": "First Pointing Moment",
        "first_date": date.today().isoformat(),
        "linked_observation_id": res_json["id"]
    }
    response = client.post(f"/insights/{child.id}/firsts", json=first_payload)
    assert response.status_code == 201
    first_res = response.json()
    assert first_res["first_title"] == "First Pointing Moment"
    assert first_res["is_first"] is True

    # H. Test Firsts confirmed list has 1 item now
    response = client.get(f"/insights/{child.id}/firsts")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["first_title"] == "First Pointing Moment"
