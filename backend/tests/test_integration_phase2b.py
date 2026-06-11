import uuid
from datetime import datetime, date, timedelta
from app.models.models import Parent, Child, Observation, ObservationType, DevelopmentalDomain, ClinicalVisit
from app.services.report_service import generate_report

def test_observation_stats_endpoint(client, db):
    # 1. Setup mock parent and child
    parent = Parent(first_name="Jane", last_name="Doe", email="stats.parent@example.com")
    db.add(parent)
    db.commit()
    db.refresh(parent)

    child = Child(first_name="Sample", last_name="Child", date_of_birth=date(2024, 6, 15), gender="Female")
    db.add(child)
    db.commit()
    db.refresh(child)

    # Fetch a domain
    domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.name == "Communication").first()
    domain_id = domain.id if domain else None

    # 2. Add multiple observations of different types
    obs1 = Observation(
        child_id=child.id,
        parent_id=parent.id,
        body="Concern log 1",
        entry_type=ObservationType.CONCERN,
        domain_id=domain_id,
        observed_at=datetime.utcnow()
    )
    obs2 = Observation(
        child_id=child.id,
        parent_id=parent.id,
        body="Milestone log 1",
        entry_type=ObservationType.MILESTONE,
        domain_id=domain_id,
        observed_at=datetime.utcnow()
    )
    obs3 = Observation(
        child_id=child.id,
        parent_id=parent.id,
        body="General log 1",
        entry_type=ObservationType.GENERAL,
        domain_id=domain_id,
        observed_at=datetime.utcnow()
    )
    db.add_all([obs1, obs2, obs3])
    db.commit()

    # 3. Call GET stats endpoint
    response = client.get(f"/children/{child.id}/observations/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_count"] == 3
    assert stats["active_concern_count"] == 1
    assert stats["by_type"]["concern"] == 1
    assert stats["by_type"]["milestone"] == 1
    assert stats["by_type"]["general"] == 1
    if domain:
        assert stats["by_domain"]["Communication"] == 3

def test_observation_filters(client, db):
    # Setup parent and child
    parent = Parent(first_name="Jane", last_name="Doe", email="filter.parent@example.com")
    db.add(parent)
    child = Child(first_name="Sample", last_name="Child", date_of_birth=date(2024, 6, 15), gender="Female")
    db.add(child)
    db.commit()
    db.refresh(parent)
    db.refresh(child)

    comm_domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.name == "Communication").first()
    motor_domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.name == "Gross Motor").first()

    # Create logs with different dates and domains
    today = datetime.utcnow()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)

    obs1 = Observation(
        child_id=child.id,
        parent_id=parent.id,
        body="Log communication concern today",
        entry_type=ObservationType.CONCERN,
        domain_id=comm_domain.id if comm_domain else None,
        observed_at=today
    )
    obs2 = Observation(
        child_id=child.id,
        parent_id=parent.id,
        body="Log motor milestone yesterday",
        entry_type=ObservationType.MILESTONE,
        domain_id=motor_domain.id if motor_domain else None,
        observed_at=yesterday
    )
    obs3 = Observation(
        child_id=child.id,
        parent_id=parent.id,
        body="Log motor general last week",
        entry_type=ObservationType.GENERAL,
        domain_id=motor_domain.id if motor_domain else None,
        observed_at=last_week
    )
    db.add_all([obs1, obs2, obs3])
    db.commit()

    # 1. Filter by domain ID
    if motor_domain:
        res = client.get(f"/children/{child.id}/observations?domain_id={motor_domain.id}")
        assert res.status_code == 200
        items = res.json()
        assert len(items) == 2
        assert all(i["domain_id"] == motor_domain.id for i in items)

    # 2. Filter by entry type
    res = client.get(f"/children/{child.id}/observations?entry_type=concern")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 1
    assert items[0]["entry_type"] == "concern"

    # 3. Filter by date range (start/end)
    start_date = (yesterday - timedelta(hours=1)).date().isoformat()
    end_date = (today + timedelta(hours=1)).date().isoformat()
    res = client.get(f"/children/{child.id}/observations?date_start={start_date}&date_end={end_date}")
    assert res.status_code == 200
    items = res.json()
    # Should contain obs1 and obs2, but exclude obs3 (last week)
    assert len(items) == 2
    assert any("today" in i["body"] for i in items)
    assert any("yesterday" in i["body"] for i in items)
    assert not any("last week" in i["body"] for i in items)

def test_visit_context_endpoints(client, db):
    # Setup child
    child = Child(first_name="Sample", last_name="Child", date_of_birth=date(2024, 6, 15), gender="Female")
    db.add(child)
    db.commit()
    db.refresh(child)

    # 1. Create a visit prep context
    visit_payload = {
        "child_id": str(child.id),
        "visit_date": "2026-06-25",
        "clinician_name": "Dr. Evelyn Marcus",
        "visit_priority": "consultation",
        "concern_level": "medium",
        "concern_note": "Primary concern details text."
    }
    create_res = client.post("/visits", json=visit_payload)
    assert create_res.status_code == 201
    created_visit = create_res.json()
    assert created_visit["clinician_name"] == "Dr. Evelyn Marcus"
    assert created_visit["visit_priority"] == "consultation"

    # 2. List child visits
    list_res = client.get(f"/visits/children/{child.id}")
    assert list_res.status_code == 200
    visits_list = list_res.json()
    assert len(visits_list) == 1
    assert visits_list[0]["id"] == created_visit["id"]
    assert visits_list[0]["clinician_name"] == "Dr. Evelyn Marcus"

def test_report_provenance_traceability(client, db):
    # Setup parent, child and clinical visit
    parent = Parent(first_name="Jane", last_name="Doe", email="trace.parent@example.com")
    db.add(parent)
    child = Child(first_name="Sample", last_name="Child", date_of_birth=date(2024, 6, 15), gender="Female")
    db.add(child)
    db.commit()
    db.refresh(parent)
    db.refresh(child)

    comm_domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.name == "Communication").first()

    # Add a concern observation
    obs = Observation(
        child_id=child.id,
        parent_id=parent.id,
        body="Traceable communication concern log",
        entry_type=ObservationType.CONCERN,
        domain_id=comm_domain.id if comm_domain else None,
        observed_at=datetime.utcnow() - timedelta(days=2)
    )
    db.add(obs)
    
    # Save a clinical visit
    visit = ClinicalVisit(
        child_id=child.id,
        visit_date=date(2026, 6, 25),
        clinician_name="Dr. Evelyn Marcus",
        visit_priority="consultation",
        concern_level="medium",
        concern_note="Discussion notes here"
    )
    db.add(visit)
    db.commit()
    db.refresh(obs)
    db.refresh(visit)

    # 1. Call POST /reports endpoint to generate snapshot
    report_payload = {
        "child_id": str(child.id),
        "visit_id": str(visit.id)
    }
    res = client.post("/reports", json=report_payload)
    assert res.status_code == 201
    report = res.json()
    
    # Verify report structure
    report_json = report["report_json"]
    assert "report_sections" in report_json
    assert "evidence" in report_json
    
    # Check that evidence list contains our observation
    evidence_logs = report_json["evidence"]
    assert len(evidence_logs) == 1
    assert evidence_logs[0]["id"] == str(obs.id)
    assert evidence_logs[0]["body"] == "Traceable communication concern log"

    # Check report sections contains concern category with matching source_observations mapping
    sections = report_json["report_sections"]
    concern_section = next(s for s in sections if s["section_key"] == "primary_concerns")
    assert concern_section["observation_count"] == 1
    assert concern_section["period_start"] is not None
    assert concern_section["period_end"] is not None
    assert len(concern_section["source_observations"]) == 1
    assert concern_section["source_observations"][0]["id"] == str(obs.id)
    assert concern_section["source_observations"][0]["contribution"] == "primary_evidence"
