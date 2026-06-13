import uuid
from datetime import datetime, date
from app.models.models import Parent, Child, InteractionType, AISuggestionEvent, Milestone, SuggestionFeedback, HumanValidationSession, parent_child_links
from app.services.ai_service import ai_engine

def test_feedback_creation_success(client, db):
    # Initialize cache
    ai_engine.initialize_cache(db)

    # 1. Create Parent and Child
    parent = db.query(Parent).order_by(Parent.created_at.desc()).first()
    child = Child(first_name="Eli", last_name="Carter", date_of_birth=date(2024, 6, 15), gender="Male")
    db.add(child)
    db.commit()
    db.refresh(child)

    # Link parent and child
    db.execute(
        parent_child_links.insert().values(
            parent_id=parent.id,
            child_id=child.id,
            relationship_type="parent"
        )
    )
    db.commit()

    # Get a milestone ID
    milestone = db.query(Milestone).first()

    payload = {
        "parent_id": str(parent.id),
        "child_id": str(child.id),
        "ai_suggestion_event_id": None,
        "milestone_id": str(milestone.id),
        "feedback_type": "helpful",
        "comment": "Very accurate match!"
    }

    response = client.post("/feedback", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["feedback_type"] == "helpful"
    assert data["comment"] == "Very accurate match!"
    assert data["milestone_id"] == str(milestone.id)

    # Verify db state
    feedback_db = db.query(SuggestionFeedback).filter(SuggestionFeedback.id == uuid.UUID(data["id"])).first()
    assert feedback_db is not None
    assert feedback_db.comment == "Very accurate match!"


def test_feedback_creation_invalid_ownership(client, db):
    # Create a parent who will own the child link
    owner_parent = Parent(first_name="Owner", last_name="Parent", email="owner.parent@example.com")
    db.add(owner_parent)
    child = Child(first_name="Eli", last_name="Carter", date_of_birth=date(2024, 6, 15), gender="Male")
    db.add(child)
    db.commit()
    db.refresh(owner_parent)
    db.refresh(child)

    # Link owner parent to child
    db.execute(
        parent_child_links.insert().values(
            parent_id=owner_parent.id,
            child_id=child.id,
            relationship_type="parent"
        )
    )
    db.commit()

    # Create another parent who will be the logged-in parent (created last, so it's the newest)
    logged_in_parent = Parent(first_name="LoggedIn", last_name="Parent", email="loggedin.parent@example.com")
    db.add(logged_in_parent)
    db.commit()
    db.refresh(logged_in_parent)

    milestone = db.query(Milestone).first()

    # Logged in parent is the default test parent (who does NOT have access to this child)
    payload = {
        "parent_id": str(owner_parent.id),
        "child_id": str(child.id),
        "ai_suggestion_event_id": None,
        "milestone_id": str(milestone.id),
        "feedback_type": "not_helpful",
        "comment": "Wrong child context"
    }

    # Should raise 403 because current logged in parent has no access to this child profile
    response = client.post("/feedback", json=payload)
    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"]


def test_validation_session_study(client, db):
    payload = {
        "participant_id": "STUDY-PARTICIPANT-01",
        "role": "Clinician",
        "usability_score": 5,
        "trust_score": 4,
        "report_usefulness_score": 5,
        "comments": "Excellent OIE transliteration explainability."
    }

    response = client.post("/validation-study", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["participant_id"] == "STUDY-PARTICIPANT-01"
    assert data["usability_score"] == 5

    # Check stats
    stats_resp = client.get("/validation-study/stats")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert stats["total_sessions"] >= 1
    assert stats["avg_usability"] >= 1.0
    assert stats["by_role"]["Clinician"] >= 1


def test_explainability_suggest_response(client, db):
    ai_engine.initialize_cache(db)
    parent = db.query(Parent).order_by(Parent.created_at.desc()).first()
    child = Child(first_name="Mini", last_name="Carter", date_of_birth=date(2024, 6, 15), gender="Female")
    db.add(child)
    db.commit()
    db.refresh(child)

    # Link parent
    db.execute(
        parent_child_links.insert().values(
            parent_id=parent.id,
            child_id=child.id,
            relationship_type="parent"
        )
    )
    db.commit()

    payload = {
        "observation_text": "She ishaara when she wanted a gudiya doll.",
        "child_id": str(child.id),
        "child_age_months": 24
    }

    response = client.post("/ai/suggest", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "milestones" in data
    
    first_suggestion = data["milestones"][0]
    assert "translated_terms" in first_suggestion
    assert "domain_name" in first_suggestion
    assert "age_band_relevance" in first_suggestion
    assert "explanation_text" in first_suggestion
    
    # Confirm transliteration glossary detected our Hinglish words
    translated = first_suggestion["translated_terms"]
    assert any(t["raw"] == "ishaara" for t in translated)
    assert any(t["raw"] == "gudiya" for t in translated)


def test_caregiver_and_judge_analytics(client, db):
    parent = db.query(Parent).order_by(Parent.created_at.desc()).first()
    child = Child(first_name="Mini", last_name="Carter", date_of_birth=date(2024, 6, 15), gender="Female")
    db.add(child)
    db.commit()
    db.refresh(child)

    # Link parent
    db.execute(
        parent_child_links.insert().values(
            parent_id=parent.id,
            child_id=child.id,
            relationship_type="parent"
        )
    )
    db.commit()

    # Trigger OIE suggests
    ai_engine.initialize_cache(db)
    client.post("/ai/suggest", json={
        "observation_text": "She points to ask for objects and smiles.",
        "child_id": str(child.id),
        "child_age_months": 15
    })

    # Fetch caregiver stats
    cg_resp = client.get(f"/analytics/caregiver/{child.id}")
    assert cg_resp.status_code == 200
    cg_data = cg_resp.json()
    assert cg_data["suggestions_reviewed"] >= 1
    assert cg_data["helpful_votes"] == 0

    # Fetch judge stats
    jg_resp = client.get("/analytics/judge")
    assert jg_resp.status_code == 200
    jg_data = jg_resp.json()
    assert jg_data["total_suggestions"] >= 1
    assert "benchmark_metrics" in jg_data
    assert jg_data["benchmark_metrics"]["top_1_accuracy"] == 0.8062
