import uuid
from datetime import datetime, date
from app.models.models import Parent, Child, InteractionType, AISuggestionEvent, Milestone, DevelopmentalDomain
from app.services.ai_service import ai_engine

def test_ai_suggest_endpoint_success(client, db):
    # Initialize cache
    ai_engine.initialize_cache(db)

    # Create Parent and Child
    parent = Parent(first_name="Test", last_name="Parent", email="endpoint.test.parent@example.com")
    db.add(parent)
    db.commit()
    db.refresh(parent)

    child = Child(first_name="Eli", last_name="Carter", date_of_birth=date(2024, 6, 15), gender="Male")
    db.add(child)
    db.commit()
    db.refresh(child)

    payload = {
        "observation_text": "He pointed to ask for something.",
        "child_id": str(child.id),
        "child_age_months": 15
    }

    response = client.post("/ai/suggest", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "domains" in data
    assert "milestones" in data
    assert "observation_patterns" in data
    assert "report_keywords" in data
    assert "explanations" in data
    assert "event_id" in data
    assert data["model_version"] == "oie_v1_multilingual"
    
    # Verify suggestions
    assert len(data["domains"]) > 0
    assert len(data["milestones"]) > 0
    assert any("point" in m["title"].lower() for m in data["milestones"])

    # Verify event was created in database
    event_id = data["event_id"]
    event_db = db.query(AISuggestionEvent).filter(AISuggestionEvent.id == uuid.UUID(event_id)).first()
    assert event_db is not None
    assert event_db.child_id == child.id
    assert event_db.raw_text == payload["observation_text"]
    assert event_db.interaction_type == InteractionType.IGNORED


def test_ai_suggest_endpoint_invalid_child(client, db):
    payload = {
        "observation_text": "He pointed to ask for something.",
        "child_id": str(uuid.uuid4()),
        "child_age_months": 15
    }
    response = client.post("/ai/suggest", json=payload)
    assert response.status_code == 404
    assert "Child profile not found." in response.json()["detail"]


def test_ai_suggest_endpoint_empty_observation(client, db):
    parent = Parent(first_name="Test", last_name="Parent", email="endpoint.test.parent2@example.com")
    db.add(parent)
    db.commit()
    db.refresh(parent)

    child = Child(first_name="Eli", last_name="Carter", date_of_birth=date(2024, 6, 15), gender="Male")
    db.add(child)
    db.commit()
    db.refresh(child)

    payload = {
        "observation_text": "   ",  # Whitespace / empty
        "child_id": str(child.id),
        "child_age_months": 24
    }
    response = client.post("/ai/suggest", json=payload)
    assert response.status_code == 422


def test_ai_confirm_endpoint_success(client, db):
    # Initialize cache
    ai_engine.initialize_cache(db)

    # Create child
    child = Child(first_name="Eli", last_name="Carter", date_of_birth=date(2024, 6, 15), gender="Male")
    db.add(child)
    db.commit()
    db.refresh(child)

    # Run suggest to create event
    payload = {
        "observation_text": "He pointed to ask for something.",
        "child_id": str(child.id),
        "child_age_months": 15
    }
    suggest_resp = client.post("/ai/suggest", json=payload)
    assert suggest_resp.status_code == 200
    event_id = suggest_resp.json()["event_id"]
    milestone_id = suggest_resp.json()["milestones"][0]["milestone_id"]

    # Confirm event
    confirm_payload = {
        "selected_domain": "Communication",
        "selected_milestone_id": milestone_id,
        "interaction_type": InteractionType.ACCEPTED
    }
    confirm_resp = client.post(f"/ai/confirm/{event_id}", json=confirm_payload)
    assert confirm_resp.status_code == 200
    confirm_data = confirm_resp.json()
    assert confirm_data["interaction_type"] == InteractionType.ACCEPTED
    assert confirm_data["selected_domain"] == "Communication"
    assert confirm_data["selected_milestone_id"] == milestone_id
    assert confirm_data["accepted_at"] is not None

    # Verify DB state
    event_db = db.query(AISuggestionEvent).filter(AISuggestionEvent.id == uuid.UUID(event_id)).first()
    assert event_db.interaction_type == InteractionType.ACCEPTED
    assert event_db.selected_domain == "Communication"
    assert str(event_db.selected_milestone_id) == milestone_id


def test_ai_confirm_endpoint_invalid_event(client, db):
    confirm_payload = {
        "selected_domain": "Communication",
        "selected_milestone_id": str(uuid.uuid4()),
        "interaction_type": InteractionType.ACCEPTED
    }
    response = client.post(f"/ai/confirm/{uuid.uuid4()}", json=confirm_payload)
    assert response.status_code == 404
    assert "AI suggestion event not found." in response.json()["detail"]


def test_ai_events_retrieval(client, db):
    # Initialize cache
    ai_engine.initialize_cache(db)

    # Create child
    child = Child(first_name="Eli", last_name="Carter", date_of_birth=date(2024, 6, 15), gender="Male")
    db.add(child)
    db.commit()
    db.refresh(child)

    # Trigger suggestions
    client.post("/ai/suggest", json={
        "observation_text": "He pointed to ask for something.",
        "child_id": str(child.id),
        "child_age_months": 15
    })
    client.post("/ai/suggest", json={
        "observation_text": "He runs easily without falling in the playground.",
        "child_id": str(child.id),
        "child_age_months": 24
    })

    # Retrieve events
    events_resp = client.get(f"/ai/events/{child.id}")
    assert events_resp.status_code == 200
    events = events_resp.json()
    assert len(events) == 2
    # Check ordering (newest first)
    assert events[0]["raw_text"] == "He runs easily without falling in the playground."


def test_ai_metrics_endpoint(client, db):
    # Initialize cache
    ai_engine.initialize_cache(db)

    # Create child
    child = Child(first_name="Eli", last_name="Carter", date_of_birth=date(2024, 6, 15), gender="Male")
    db.add(child)
    db.commit()
    db.refresh(child)

    # 1. Suggestion 1: ACCEPTED
    res1 = client.post("/ai/suggest", json={
        "observation_text": "He pointed to ask for something.",
        "child_id": str(child.id),
        "child_age_months": 15
    })
    event_id1 = res1.json()["event_id"]
    milestone_id1 = res1.json()["milestones"][0]["milestone_id"]
    client.post(f"/ai/confirm/{event_id1}", json={
        "selected_domain": "Communication",
        "selected_milestone_id": milestone_id1,
        "interaction_type": InteractionType.ACCEPTED
    })

    # 2. Suggestion 2: OVERRIDDEN
    res2 = client.post("/ai/suggest", json={
        "observation_text": "He runs easily without falling in the playground.",
        "child_id": str(child.id),
        "child_age_months": 24
    })
    event_id2 = res2.json()["event_id"]
    client.post(f"/ai/confirm/{event_id2}", json={
        "selected_domain": "Communication", # override domain
        "selected_milestone_id": milestone_id1, # override milestone
        "interaction_type": InteractionType.OVERRIDDEN
    })

    # 3. Suggestion 3: IGNORED (no confirmation post)
    client.post("/ai/suggest", json={
        "observation_text": "He looks at my face when I talk to him and smiles.",
        "child_id": str(child.id),
        "child_age_months": 24
    })

    # Fetch metrics
    metrics_resp = client.get(f"/ai/metrics/{child.id}")
    assert metrics_resp.status_code == 200
    metrics = metrics_resp.json()
    
    assert metrics["total_suggestions"] == 3
    assert metrics["accepted"] == 1
    assert metrics["overridden"] == 1
    assert metrics["ignored"] == 1
    assert metrics["manual_only"] == 0
    assert abs(metrics["acceptance_rate"] - 0.3333) < 1e-3
    assert "Communication" in metrics["top_domains"]
    assert len(metrics["top_milestones"]) == 1
    assert "Points" in metrics["top_milestones"][0]
