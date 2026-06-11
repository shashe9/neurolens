import uuid
from datetime import date, datetime, timedelta
from app.models.models import Parent, Child, Observation, ObservationType, ClinicalVisit

def test_child_profile_crud_lifecycle(client, db):
    # 1. Seed Parent
    parent = Parent(first_name="Jane", last_name="Doe", email="crud.parent@example.com")
    db.add(parent)
    db.commit()
    db.refresh(parent)

    # 2. Test Create: Validation Failure (empty name)
    child_payload = {
        "first_name": "  ",
        "last_name": "Doe",
        "date_of_birth": "2024-06-15",
        "parent_id": str(parent.id)
    }
    res = client.post("/children", json=child_payload)
    assert res.status_code == 422

    # 3. Test Create: Optional Gender
    child_payload = {
        "first_name": "Timmy",
        "last_name": "Doe",
        "date_of_birth": "2024-06-15",
        "gender": "",  # Empty string/Optional
        "parent_id": str(parent.id)
    }
    res = client.post("/children", json=child_payload)
    assert res.status_code == 201
    child_data = res.json()
    child_id = child_data["id"]
    assert child_data["first_name"] == "Timmy"
    assert child_data["gender"] is None  # Resolved to None/null

    # 4. Test Edit (PUT /children/{id})
    update_payload = {
        "first_name": "Timothy",
        "gender": "Male"
    }
    res = client.put(f"/children/{child_id}", json=update_payload)
    assert res.status_code == 200
    updated_data = res.json()
    assert updated_data["first_name"] == "Timothy"
    assert updated_data["gender"] == "Male"
    # Ensure DOB remained unchanged
    assert updated_data["date_of_birth"] == "2024-06-15"

    # 5. Test Soft Delete (Archive)
    res = client.delete(f"/children/{child_id}?deleted_by={parent.id}")
    assert res.status_code == 200
    archived_data = res.json()
    assert archived_data["deleted_at"] is not None
    assert archived_data["deleted_by"] == str(parent.id)

    # 6. Verify archived child is hidden by default
    res = client.get(f"/children?parent_id={parent.id}")
    assert res.status_code == 200
    assert len(res.json()) == 0

    # 7. Verify archived child is returned if include_archived=true
    res = client.get(f"/children?parent_id={parent.id}&include_archived=true")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["id"] == child_id

    # 8. Test Restore
    res = client.post(f"/children/{child_id}/restore")
    assert res.status_code == 200
    restored_data = res.json()
    assert restored_data["deleted_at"] is None
    assert restored_data["deleted_by"] is None

    # Verify visible again
    res = client.get(f"/children?parent_id={parent.id}")
    assert len(res.json()) == 1

def test_report_ownership_validation(client, db):
    # 1. Setup Parent
    parent = Parent(first_name="Jane", last_name="Doe", email="owner.parent@example.com")
    db.add(parent)
    db.commit()
    db.refresh(parent)

    # 2. Setup Child A and Child B
    child_a = Child(first_name="Child", last_name="A", date_of_birth=date(2024, 6, 15), gender="Male")
    child_b = Child(first_name="Child", last_name="B", date_of_birth=date(2024, 6, 15), gender="Female")
    db.add_all([child_a, child_b])
    db.commit()
    db.refresh(child_a)
    db.refresh(child_b)

    # 3. Create Clinical Visit for Child B
    visit = ClinicalVisit(
        child_id=child_b.id,
        visit_date=date(2026, 6, 25),
        clinician_name="Dr. Evelyn Marcus",
        visit_priority="consultation",
        concern_level="medium",
        concern_note="Visit notes for Child B."
    )
    db.add(visit)
    db.commit()
    db.refresh(visit)

    # 4. Attempt to generate report for Child A using Child B's visit context
    report_payload = {
        "child_id": str(child_a.id),
        "visit_id": str(visit.id)
    }
    res = client.post("/reports", json=report_payload)
    # ValueError from report service is handled as a 404 error
    assert res.status_code == 404
    assert "does not match the specified child" in res.json()["detail"]

def test_cross_child_evidence_isolation(client, db):
    # 1. Setup Parent
    parent = Parent(first_name="Jane", last_name="Doe", email="isolation.parent@example.com")
    db.add(parent)
    db.commit()
    db.refresh(parent)

    # 2. Setup Child A and Child B
    child_a = Child(first_name="Child", last_name="A", date_of_birth=date(2024, 6, 15), gender="Male")
    child_b = Child(first_name="Child", last_name="B", date_of_birth=date(2024, 6, 15), gender="Female")
    db.add_all([child_a, child_b])
    db.commit()
    db.refresh(child_a)
    db.refresh(child_b)

    # 3. Log 5 observations for Child A
    obs_a_ids = []
    for i in range(5):
        obs = Observation(
            child_id=child_a.id,
            parent_id=parent.id,
            body=f"Observation Child A log {i}",
            entry_type=ObservationType.GENERAL,
            observed_at=datetime.utcnow() - timedelta(hours=i)
        )
        db.add(obs)
        db.commit()
        db.refresh(obs)
        obs_a_ids.append(str(obs.id))

    # 4. Log 5 observations for Child B
    obs_b_ids = []
    for i in range(5):
        obs = Observation(
            child_id=child_b.id,
            parent_id=parent.id,
            body=f"Observation Child B log {i}",
            entry_type=ObservationType.GENERAL,
            observed_at=datetime.utcnow() - timedelta(hours=i)
        )
        db.add(obs)
        db.commit()
        db.refresh(obs)
        obs_b_ids.append(str(obs.id))

    # 5. Generate reports for both
    res_a = client.post("/reports", json={"child_id": str(child_a.id)})
    res_b = client.post("/reports", json={"child_id": str(child_b.id)})
    assert res_a.status_code == 201
    assert res_b.status_code == 201

    report_a_json = res_a.json()["report_json"]
    report_b_json = res_b.json()["report_json"]

    # 6. Verify evidence isolation
    evidence_a = [e["id"] for e in report_a_json["evidence"]]
    evidence_b = [e["id"] for e in report_b_json["evidence"]]

    assert len(evidence_a) == 5
    assert len(evidence_b) == 5
    
    # No crossover check
    assert not any(obs_id in evidence_b for obs_id in evidence_a)
    assert all(obs_id in evidence_a for obs_id in obs_a_ids)
    assert all(obs_id in evidence_b for obs_id in obs_b_ids)

    # 7. Verify report sections provenance isolation
    sections_a = report_a_json["report_sections"]
    sections_b = report_b_json["report_sections"]

    gen_sec_a = next(s for s in sections_a if s["section_key"] == "general_logs")
    gen_sec_b = next(s for s in sections_b if s["section_key"] == "general_logs")

    assert gen_sec_a["observation_count"] == 5
    assert gen_sec_b["observation_count"] == 5

    source_a = [o["id"] for o in gen_sec_a["source_observations"]]
    source_b = [o["id"] for o in gen_sec_b["source_observations"]]

    assert not any(source_id in source_b for source_id in source_a)
    assert all(obs_id in source_a for obs_id in obs_a_ids)
    assert all(obs_id in source_b for obs_id in obs_b_ids)
