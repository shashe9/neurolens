import uuid
from datetime import date, datetime
from app.models.models import Parent, Child, Milestone
from app.services.report_service import generate_report

def test_complete_report_workflow(client, db):
    # 1. Create Parent directly in DB session
    parent = Parent(
        first_name="Sarah",
        last_name="Carter",
        email="sarah.carter@example.com"
    )
    db.add(parent)
    db.commit()
    db.refresh(parent)
    assert parent.id is not None

    # 2. POST /children (link to Parent)
    child_payload = {
        "first_name": "Leo",
        "last_name": "Carter",
        "date_of_birth": "2024-06-15",
        "gender": "Male",
        "parent_id": str(parent.id)
    }
    response = client.post("/children", json=child_payload)
    assert response.status_code == 201
    child_data = response.json()
    child_id = child_data["id"]
    assert child_data["first_name"] == "Leo"

    # 3. GET /children/{id}
    get_child_resp = client.get(f"/children/{child_id}")
    assert get_child_resp.status_code == 200
    assert get_child_resp.json()["last_name"] == "Carter"

    # 4. POST /children/{child_id}/observations (General Observation)
    obs_payload = {
        "parent_id": str(parent.id),
        "body": "Played with blocks for 15 minutes. Showed good persistence.",
        "entry_type": "general",
        "observed_at": datetime.utcnow().isoformat(),
        "context_note": "Living room during playtime",
        "is_regression": False
    }
    obs_response = client.post(f"/children/{child_id}/observations", json=obs_payload)
    assert obs_response.status_code == 201
    obs_data = obs_response.json()
    assert obs_data["body"] == obs_payload["body"]
    assert obs_data["entry_type"] == "general"

    # 5. GET /children/{child_id}/observations (check listing)
    list_obs_resp = client.get(f"/children/{child_id}/observations")
    assert list_obs_resp.status_code == 200
    assert len(list_obs_resp.json()) == 1

    # 6. POST /visits (Visit Context preparation)
    visit_payload = {
        "child_id": child_id,
        "visit_date": "2026-06-25",
        "clinician_name": "Dr. Evelyn Marcus",
        "visit_priority": "consultation",
        "concern_level": "medium",
        "concern_note": "Discuss responding to name calls and verbal queries."
    }
    visit_response = client.post("/visits", json=visit_payload)
    assert visit_response.status_code == 201
    visit_data = visit_response.json()
    visit_id = visit_data["id"]
    assert visit_data["clinician_name"] == "Dr. Evelyn Marcus"

    # 7. POST /reports (Initiate Report compilation snapshot)
    report_payload = {
        "child_id": child_id,
        "visit_id": visit_id
    }
    report_response = client.post("/reports", json=report_payload)
    assert report_response.status_code == 201
    report_data = report_response.json()
    report_id = report_data["id"]
    
    # Assert report snapshot details
    assert report_data["status"] == "final"
    report_json = report_data["report_json"]
    assert report_json["child"]["first_name"] == "Leo"
    assert report_json["parents"][0]["email"] == "sarah.carter@example.com"
    assert report_json["visit_context"]["clinician"] == "Dr. Evelyn Marcus"
    assert len(report_json["evidence"]) == 1

    # 8. GET /reports/{id} (Check persistence of finalized report)
    get_report_resp = client.get(f"/reports/{report_id}")
    assert get_report_resp.status_code == 200
    assert get_report_resp.json()["report_json"]["child"]["last_name"] == "Carter"
