import uuid
from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import (
    Parent,
    Child,
    Milestone,
    DevelopmentalDomain,
    Observation,
    ObservationType,
    MilestoneStatus,
    ObservationMilestoneEvidence
)

@pytest.fixture
def setup_test_data(db: Session):
    # Setup domains
    domain_comm = DevelopmentalDomain(name="Communication Test", description="Comm testing")
    domain_motor = DevelopmentalDomain(name="Motor Test", description="Motor testing")
    db.add(domain_comm)
    db.add(domain_motor)
    db.commit()
    db.refresh(domain_comm)
    db.refresh(domain_motor)

    # Setup parent
    parent = Parent(first_name="Alice", last_name="Smith", email="alice.smith@example.com")
    db.add(parent)
    db.commit()
    db.refresh(parent)

    # Setup Child A (Active)
    child_a = Child(first_name="Child", last_name="A", date_of_birth=datetime.utcnow().date() - timedelta(days=730)) # 2 years old
    db.add(child_a)
    db.commit()
    db.refresh(child_a)
    child_a.parents.append(parent)

    # Setup Child B (Active)
    child_b = Child(first_name="Child", last_name="B", date_of_birth=datetime.utcnow().date() - timedelta(days=540)) # 1.5 years old
    db.add(child_b)
    db.commit()
    db.refresh(child_b)
    child_b.parents.append(parent)

    # Setup Child C (Archived/Soft-Deleted)
    child_c = Child(
        first_name="Child", 
        last_name="C", 
        date_of_birth=datetime.utcnow().date() - timedelta(days=730),
        deleted_at=datetime.utcnow(),
        deleted_by=parent.id
    )
    db.add(child_c)
    db.commit()
    db.refresh(child_c)
    child_c.parents.append(parent)

    # Setup global milestones
    m1 = Milestone(domain_id=domain_comm.id, title="Milestone 1", description="Description 1", age_range_low=18, age_range_high=24)
    m2 = Milestone(domain_id=domain_comm.id, title="Milestone 2", description="Description 2", age_range_low=18, age_range_high=24)
    m3 = Milestone(domain_id=domain_motor.id, title="Milestone 3", description="Description 3", age_range_low=18, age_range_high=24)
    db.add_all([m1, m2, m3])
    db.commit()
    db.refresh(m1)
    db.refresh(m2)
    db.refresh(m3)

    db.commit()

    return {
        "parent_id": parent.id,
        "child_a_id": child_a.id,
        "child_b_id": child_b.id,
        "child_c_id": child_c.id,
        "m1_id": m1.id,
        "m2_id": m2.id,
        "m3_id": m3.id,
        "comm_id": domain_comm.id,
        "motor_id": domain_motor.id
    }

def test_evidence_linking_and_unlinking(client: TestClient, db: Session, setup_test_data):
    data = setup_test_data
    child_a_id = data["child_a_id"]
    m1_id = data["m1_id"]

    # 1. Create parent observation for Child A
    obs_res = client.post(
        f"/children/{child_a_id}/observations",
        json={
            "parent_id": str(data["parent_id"]),
            "body": "Child A demonstrated skill matching milestone 1",
            "entry_type": "milestone",
            "domain_id": data["comm_id"],
            "observed_at": datetime.utcnow().isoformat()
        }
    )
    assert obs_res.status_code == 201
    obs_id = obs_res.json()["id"]

    # 2. Link observation to milestone 1
    link_res = client.post(
        f"/children/{child_a_id}/milestones/{m1_id}/evidence",
        json={"observation_id": obs_id}
    )
    assert link_res.status_code == 200
    assert link_res.json()["observation_id"] == obs_id
    assert link_res.json()["milestone_id"] == str(m1_id)

    # Verify connection exists in DB
    evidence_count = db.query(ObservationMilestoneEvidence).filter_by(
        observation_id=uuid.UUID(obs_id), milestone_id=m1_id
    ).count()
    assert evidence_count == 1

    # 3. Retrieve milestones and verify evidence is listed
    milestones_res = client.get(f"/children/{child_a_id}/milestones")
    assert milestones_res.status_code == 200
    m_list = milestones_res.json()
    m1_data = next(m for m in m_list if m["id"] == str(m1_id))
    assert m1_data["evidence_count"] == 1
    assert obs_id in m1_data["evidence_ids"]
    assert m1_data["evidence"][0]["body"] == "Child A demonstrated skill matching milestone 1"

    # 4. Unlink evidence
    unlink_res = client.delete(f"/children/{child_a_id}/milestones/{m1_id}/evidence/{obs_id}")
    assert unlink_res.status_code == 200
    assert unlink_res.json()["status"] == "success"

    # Verify connection is deleted from DB
    evidence_count = db.query(ObservationMilestoneEvidence).filter_by(
        observation_id=uuid.UUID(obs_id), milestone_id=m1_id
    ).count()
    assert evidence_count == 0

def test_duplicate_linking_prevention(client: TestClient, setup_test_data):
    data = setup_test_data
    child_a_id = data["child_a_id"]
    m1_id = data["m1_id"]

    obs_res = client.post(
        f"/children/{child_a_id}/observations",
        json={
            "parent_id": str(data["parent_id"]),
            "body": "Child A demonstrated skill",
            "entry_type": "milestone",
            "domain_id": data["comm_id"],
            "observed_at": datetime.utcnow().isoformat()
        }
    )
    obs_id = obs_res.json()["id"]

    # First link: Success
    res1 = client.post(f"/children/{child_a_id}/milestones/{m1_id}/evidence", json={"observation_id": obs_id})
    assert res1.status_code == 200

    # Second link: Duplicate error (400 Bad Request)
    res2 = client.post(f"/children/{child_a_id}/milestones/{m1_id}/evidence", json={"observation_id": obs_id})
    assert res2.status_code == 400
    assert "already linked" in res2.json()["detail"]

def test_cross_child_linkage_rejection(client: TestClient, setup_test_data):
    data = setup_test_data
    child_a_id = data["child_a_id"]
    child_b_id = data["child_b_id"]
    m1_id = data["m1_id"]

    # Create observation belonging to Child A
    obs_res = client.post(
        f"/children/{child_a_id}/observations",
        json={
            "parent_id": str(data["parent_id"]),
            "body": "Child A observation",
            "entry_type": "milestone",
            "domain_id": data["comm_id"],
            "observed_at": datetime.utcnow().isoformat()
        }
    )
    obs_id = obs_res.json()["id"]

    # Attempt to link Child A's observation to Child B's milestones endpoint context
    # Must fail with a 400 Bad Request
    link_res = client.post(
        f"/children/{child_b_id}/milestones/{m1_id}/evidence",
        json={"observation_id": obs_id}
    )
    assert link_res.status_code == 400
    assert "child context" in link_res.json()["detail"]

def test_deleted_observation_evidence_exclusion(client: TestClient, setup_test_data):
    data = setup_test_data
    child_a_id = data["child_a_id"]
    m1_id = data["m1_id"]

    # 1. Create observation
    obs_res = client.post(
        f"/children/{child_a_id}/observations",
        json={
            "parent_id": str(data["parent_id"]),
            "body": "Child A observation to be soft deleted",
            "entry_type": "milestone",
            "domain_id": data["comm_id"],
            "observed_at": datetime.utcnow().isoformat()
        }
    )
    obs_id = obs_res.json()["id"]

    # 2. Link observation
    client.post(f"/children/{child_a_id}/milestones/{m1_id}/evidence", json={"observation_id": obs_id})

    # Verify link counts
    milestones_res = client.get(f"/children/{child_a_id}/milestones")
    m1_data = next(m for m in milestones_res.json() if m["id"] == str(m1_id))
    assert m1_data["evidence_count"] == 1

    # 3. Soft-delete the observation
    del_res = client.delete(f"/observations/{obs_id}?deleted_by={data['parent_id']}")
    assert del_res.status_code == 200

    # 4. Verify that the soft-deleted observation is now excluded from milestone evidence query lists
    milestones_res2 = client.get(f"/children/{child_a_id}/milestones")
    m1_data2 = next(m for m in milestones_res2.json() if m["id"] == str(m1_id))
    assert m1_data2["evidence_count"] == 0
    assert obs_id not in m1_data2["evidence_ids"]

def test_archived_child_fully_read_only(client: TestClient, setup_test_data):
    data = setup_test_data
    child_c_id = data["child_c_id"]  # Archived child
    m1_id = data["m1_id"]

    # 1. Attempt to update status on archived child: Blocked (400)
    status_res = client.put(
        f"/children/{child_c_id}/milestones/{m1_id}/status",
        json={"status": "emerging", "notes": "No update allowed"}
    )
    assert status_res.status_code == 400
    assert "Archived children" in status_res.json()["detail"]

    # 2. Attempt to create observation for archived child (not allowed in our business layer/endpoint if soft-deleted)
    # Wait, the soft deletion makes it read-only. Let's try linking to an observation:
    # First, let's create a stray observation under Child A (active) and try to link it to Child C's context.
    # It will fail due to cross-child ownership boundary check.
    # What if we link to an observation created prior to Child C archiving?
    # Let's bypass database validations and insert an observation manually under Child C to test linking/unlinking rules on archived.
    # Actually, we can test:
    # Let's write a test verifying that calling the link_observation_to_milestone service with Child C raises a ValueError.
    # Let's test the endpoint response:
    link_res = client.post(
        f"/children/{child_c_id}/milestones/{m1_id}/evidence",
        json={"observation_id": str(uuid.uuid4())}
    )
    assert link_res.status_code == 400
    assert "Archived children" in link_res.json()["detail"]

    # 3. Attempt to unlink evidence on archived child: Blocked (400)
    unlink_res = client.delete(
        f"/children/{child_c_id}/milestones/{m1_id}/evidence/{uuid.uuid4()}"
    )
    assert unlink_res.status_code == 400
    assert "Archived children" in unlink_res.json()["detail"]

def test_coverage_and_report_traceability(client: TestClient, setup_test_data):
    data = setup_test_data
    child_a_id = data["child_a_id"]
    m1_id = data["m1_id"]
    m2_id = data["m2_id"]

    # Log 2 observations for Child A
    now = datetime.utcnow()
    obs1_res = client.post(
        f"/children/{child_a_id}/observations",
        json={
            "parent_id": str(data["parent_id"]),
            "body": "Obs 1",
            "entry_type": "milestone",
            "domain_id": data["comm_id"],
            "observed_at": (now - timedelta(days=5)).isoformat()
        }
    )
    obs1_id = obs1_res.json()["id"]

    obs2_res = client.post(
        f"/children/{child_a_id}/observations",
        json={
            "parent_id": str(data["parent_id"]),
            "body": "Obs 2",
            "entry_type": "milestone",
            "domain_id": data["comm_id"],
            "observed_at": now.isoformat()
        }
    )
    obs2_id = obs2_res.json()["id"]

    # Link both to Milestone 1
    client.post(f"/children/{child_a_id}/milestones/{m1_id}/evidence", json={"observation_id": obs1_id})
    client.post(f"/children/{child_a_id}/milestones/{m1_id}/evidence", json={"observation_id": obs2_id})

    # Set milestone 1 status to consistently_demonstrated
    client.put(
        f"/children/{child_a_id}/milestones/{m1_id}/status",
        json={"status": "consistently_demonstrated", "notes": "Super clean"}
    )

    # 1. Verify Coverage Calculations
    coverage_res = client.get(f"/children/{child_a_id}/milestones/coverage")
    assert coverage_res.status_code == 200
    coverage = coverage_res.json()["domains"]
    
    comm_coverage = next(c for c in coverage if c["domain_name"] == "Communication Test")
    assert comm_coverage["milestone_count"] == 2
    assert comm_coverage["milestones_with_evidence"] == 1
    assert comm_coverage["milestones_without_evidence"] == 1
    assert comm_coverage["observation_count"] == 2
    assert comm_coverage["evidence_count"] == 2

    # 2. Verify Report Traceability and Structured Dates
    # Create a clinical visit for Child A
    visit_res = client.post(
        "/visits",
        json={
            "child_id": str(child_a_id),
            "visit_date": datetime.utcnow().date().isoformat(),
            "clinician_name": "Dr. Sarah",
            "visit_priority": "routine",
            "concern_level": "low",
            "concern_note": "Routine checkup"
        }
    )
    visit_id = visit_res.json()["id"]

    # Generate clinician report
    report_res = client.post(
        "/reports",
        json={
            "child_id": str(child_a_id),
            "visit_id": visit_id
        }
    )
    assert report_res.status_code == 201
    report_data = report_res.json()["report_json"]

    # Verify coverage summary block inside report JSON (Major Issue 10 recommendation)
    assert "coverage_summary" in report_data
    assert "Communication Test" in report_data["coverage_summary"]
    assert report_data["coverage_summary"]["Communication Test"]["supported_milestones"] == 1
    assert report_data["coverage_summary"]["Communication Test"]["total_milestones"] == 2
    assert report_data["coverage_summary"]["Communication Test"]["total_evidence_observations"] == 2

    # Verify structured date ranges and evidence counts inside report milestone snapshot
    m1_report = next(m for m in report_data["milestones"] if m["id"] == str(m1_id))
    assert m1_report["status"] == "consistently_demonstrated"
    assert m1_report["evidence_count"] == 2
    assert obs1_id in m1_report["evidence_observation_ids"]
    assert obs2_id in m1_report["evidence_observation_ids"]
    assert m1_report["first_evidence_date"] == (now - timedelta(days=5)).date().isoformat()
    assert m1_report["last_evidence_date"] == now.date().isoformat()
