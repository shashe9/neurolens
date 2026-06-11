import uuid
from datetime import datetime
from app.models.models import Parent, Child, Observation, ObservationType
from app.services.report_service import generate_report

def test_observation_crud_and_validation(client, db):
    # 1. Seed Parent and Child
    parent = Parent(first_name="Jane", last_name="Doe", email="test.historian@example.com")
    db.add(parent)
    db.commit()
    db.refresh(parent)
    
    child = Child(first_name="Sample", last_name="Child", date_of_birth=datetime(2024, 6, 15).date(), gender="Female")
    db.add(child)
    db.commit()
    db.refresh(child)

    # 2. Test Validation: Empty Body
    obs_payload = {
        "parent_id": str(parent.id),
        "body": "   ",
        "entry_type": "general"
    }
    response = client.post(f"/children/{child.id}/observations", json=obs_payload)
    assert response.status_code == 422
    assert "cannot be empty" in response.text

    # 3. Test Validation: Invalid Entry Type Enum
    obs_payload = {
        "parent_id": str(parent.id),
        "body": "Valid body text",
        "entry_type": "invalid_type_here"
    }
    response = client.post(f"/children/{child.id}/observations", json=obs_payload)
    assert response.status_code == 422

    # 4. Test Create (Nested Endpoint POST /children/{child_id}/observations)
    obs_payload = {
        "parent_id": str(parent.id),
        "body": "Jane observed Timmy running in the backyard.",
        "entry_type": "general",
        "location": "Backyard",
        "observer_relation": "Mother"
    }
    response = client.post(f"/children/{child.id}/observations", json=obs_payload)
    assert response.status_code == 201
    obs_data = response.json()
    obs_id = obs_data["id"]
    assert obs_data["body"] == obs_payload["body"]
    assert obs_data["location"] == "Backyard"
    assert obs_data["observer_relation"] == "Mother"

    # 5. Test Get Detail (GET /observations/{id})
    get_resp = client.get(f"/observations/{obs_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["body"] == obs_payload["body"]

    # 6. Test Update (PUT /observations/{id})
    update_payload = {
        "body": "Updated details: running in the backyard and kicked a ball.",
        "location": "Backyard Garden"
    }
    put_resp = client.put(f"/observations/{obs_id}", json=update_payload)
    assert put_resp.status_code == 200
    updated_data = put_resp.json()
    assert updated_data["body"] == update_payload["body"]
    assert updated_data["location"] == "Backyard Garden"
    # Ensure entry_type remained unchanged
    assert updated_data["entry_type"] == "general"

    # 7. Test Soft Delete (DELETE /observations/{id}?deleted_by={parent_id})
    del_resp = client.delete(f"/observations/{obs_id}?deleted_by={parent.id}")
    assert del_resp.status_code == 200
    del_data = del_resp.json()
    assert del_data["deleted_at"] is not None
    assert del_data["deleted_by"] == str(parent.id)

    # 8. Verify it does not appear in normal child list (GET /children/{child_id}/observations)
    list_resp = client.get(f"/children/{child.id}/observations")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 0

    # 9. Verify get detail now raises 404
    get_deleted_resp = client.get(f"/observations/{obs_id}")
    assert get_deleted_resp.status_code == 404


def test_report_immutability_workflow(client, db):
    """
    NEUROLENS CORE PRINCIPLE TEST:
    Reports are immutable clinical snapshots generated from a changing longitudinal record.
    """
    # 1. Seed Parent and Child
    parent = Parent(first_name="Jane", last_name="Doe", email="immutability.historian@example.com")
    db.add(parent)
    db.commit()
    db.refresh(parent)
    
    child = Child(first_name="Sample", last_name="Child", date_of_birth=datetime(2024, 6, 15).date(), gender="Female")
    db.add(child)
    db.commit()
    db.refresh(child)

    # 2. Log Observation 1
    obs_payload = {
        "parent_id": str(parent.id),
        "body": "Observation 1: Stacking rings on the table.",
        "entry_type": "general"
    }
    obs_resp = client.post(f"/children/{child.id}/observations", json=obs_payload)
    assert obs_resp.status_code == 201
    obs_1_id = obs_resp.json()["id"]

    # 3. Generate Report A (SNAPSHOT 1)
    report_a_resp = client.post("/reports", json={"child_id": str(child.id)})
    assert report_a_resp.status_code == 201
    report_a_data = report_a_resp.json()
    report_a_id = report_a_data["id"]
    
    # Assert Report A has 1 observation
    assert len(report_a_data["report_json"]["evidence"]) == 1
    assert report_a_data["report_json"]["evidence"][0]["id"] == obs_1_id
    assert report_a_data["report_json"]["evidence"][0]["body"] == "Observation 1: Stacking rings on the table."

    # 4. Soft Delete Observation 1
    del_resp = client.delete(f"/observations/{obs_1_id}?deleted_by={parent.id}")
    assert del_resp.status_code == 200

    # 5. Log Observation 2
    obs_2_payload = {
        "parent_id": str(parent.id),
        "body": "Observation 2: Walking up stairs.",
        "entry_type": "general"
    }
    obs_2_resp = client.post(f"/children/{child.id}/observations", json=obs_2_payload)
    assert obs_2_resp.status_code == 201
    obs_2_id = obs_2_resp.json()["id"]

    # 6. Generate Report B (SNAPSHOT 2)
    report_b_resp = client.post("/reports", json={"child_id": str(child.id)})
    assert report_b_resp.status_code == 201
    report_b_data = report_b_resp.json()
    report_b_id = report_b_data["id"]

    # 7. Assertions on Report B (contains only Observation 2 because Observation 1 is soft deleted)
    assert len(report_b_data["report_json"]["evidence"]) == 1
    assert report_b_data["report_json"]["evidence"][0]["id"] == obs_2_id
    assert report_b_data["report_json"]["evidence"][0]["body"] == "Observation 2: Walking up stairs."

    # 8. CRITICAL VERIFICATION: Retrieve and check Report A from DB again
    get_report_a = client.get(f"/reports/{report_a_id}")
    assert get_report_a.status_code == 200
    report_a_persisted = get_report_a.json()
    
    # Report A must remain COMPLETELY UNCHANGED, preserving Observation 1
    assert len(report_a_persisted["report_json"]["evidence"]) == 1
    assert report_a_persisted["report_json"]["evidence"][0]["id"] == obs_1_id
    assert report_a_persisted["report_json"]["evidence"][0]["body"] == "Observation 1: Stacking rings on the table."
    print("Report A immutability successfully verified!")
