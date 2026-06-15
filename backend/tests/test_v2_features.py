import uuid
from datetime import datetime, timedelta
from app.models.models import Parent, Child, Milestone, MilestoneStatus

def test_onboarding_questionnaire(client, db):
    # 1. Create a parent and child
    parent = db.query(Parent).order_by(Parent.created_at.desc()).first()
    if not parent:
        parent = Parent(
            first_name="Test",
            last_name="Parent",
            email="test.parent.new@example.com"
        )
        db.add(parent)
        db.commit()
        db.refresh(parent)

    child = Child(
        first_name="Leo",
        last_name="Carter",
        date_of_birth=datetime.utcnow().date() - timedelta(days=730), # 2 years old
        gender="Male"
    )
    db.add(child)
    db.commit()
    db.refresh(child)

    # Make sure parent-child relationship exists
    from app.models.models import parent_child_links
    is_linked = db.execute(
        parent_child_links.select().where(
            parent_child_links.c.parent_id == parent.id,
            parent_child_links.c.child_id == child.id
        )
    ).first()
    if not is_linked:
        db.execute(
            parent_child_links.insert().values(
                parent_id=parent.id,
                child_id=child.id,
                relationship_type="parent"
            )
        )
        db.commit()

    # Get some valid milestones from the seeded DB
    milestones = db.query(Milestone).limit(3).all()
    assert len(milestones) >= 3

    seeds_payload = {}
    for m in milestones:
        seeds_payload[str(m.id)] = "observed"

    # 2. Submit onboarding questionnaire
    payload = {
        "child_id": str(child.id),
        "snapshot": {
            "speaks_words": True,
            "points_to_objects": False,
            "responds_to_name": True,
            "walks_independently": True
        },
        "milestone_seeds": seeds_payload
    }

    response = client.post("/onboarding/questionnaire", json=payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert res_data["seeded_milestones_count"] == len(milestones)

    # 3. Verify Child initial_snapshot is persisted
    db.refresh(child)
    assert child.initial_snapshot == payload["snapshot"]
    assert child.initial_snapshot["speaks_words"] is True
    assert child.initial_snapshot["points_to_objects"] is False

    # 4. Verify MilestoneStatus records are seeded
    seeded_statuses = db.query(MilestoneStatus).filter(MilestoneStatus.child_id == child.id).all()
    assert len(seeded_statuses) == len(milestones)
    for status in seeded_statuses:
        assert status.status == "observed"
        assert status.observed_date is not None


def test_observation_structuring_service():
    from app.services.structuring_service import StructuringService
    service = StructuringService()
    
    # Test typical Hinglish translation fallback rephrasing
    res1 = service.structure_text("baccha khilona lane ke liye bolta hai")
    assert "Child asks to bring the toy" in res1
    
    res2 = service.structure_text("he points to the ball and says mommy")
    assert "Points" in res2 or "points" in res2


def test_observation_structuring_endpoints(client, db):
    # 1. Test draft endpoint
    draft_payload = {
        "child_id": str(uuid.uuid4()),  # dummy, not checked for draft
        "body": "baccha khilona lane ke liye bolta hai"
    }
    response = client.post("/observations/structure-draft", json=draft_payload)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["raw_body"] == draft_payload["body"]
    assert "Child asks to bring the toy" in res_data["structured_body"]
    assert res_data["status"] == "completed"

    # 2. Test create observation with auto-structuring
    parent = db.query(Parent).order_by(Parent.created_at.desc()).first()
    if not parent:
        parent = Parent(
            first_name="Test",
            last_name="Parent",
            email="test.parent.structuring@example.com"
        )
        db.add(parent)
        db.commit()
        db.refresh(parent)

    child = Child(
        first_name="Leo",
        last_name="Carter",
        date_of_birth=datetime.utcnow().date() - timedelta(days=730),
        gender="Male"
    )
    db.add(child)
    db.commit()
    db.refresh(child)

    # Link parent and child
    from app.models.models import parent_child_links
    db.execute(
        parent_child_links.insert().values(
            parent_id=parent.id,
            child_id=child.id,
            relationship_type="parent"
        )
    )
    db.commit()

    # Scenario A: Log observation with explicit rephrasing accepted by parent
    obs_payload = {
        "parent_id": str(parent.id),
        "body": "baccha khilona lane ke liye bolta hai",
        "entry_type": "general",
        "observed_at": datetime.utcnow().isoformat(),
        "structured_body": "Child asks to bring the toy.",
        "structuring_status": "approved"
    }
    create_resp = client.post(f"/children/{child.id}/observations", json=obs_payload)
    assert create_resp.status_code == 201
    obs_data = create_resp.json()
    assert obs_data["structuring_status"] == "approved"
    assert obs_data["structured_body"] == "Child asks to bring the toy."

    # Scenario B: Log raw observation without explicit rephrasing action
    raw_payload = {
        "parent_id": str(parent.id),
        "body": "Only raw note text",
        "entry_type": "general",
        "observed_at": datetime.utcnow().isoformat()
    }
    raw_resp = client.post(f"/children/{child.id}/observations", json=raw_payload)
    assert raw_resp.status_code == 201
    raw_data = raw_resp.json()
    assert raw_data["structured_body"] is None
    assert raw_data["structuring_status"] is None

    # 3. Test confirm endpoint
    confirm_payload = {
        "structured_body": "Child asks for the toy clearly.",
        "status": "approved"
    }
    confirm_resp = client.post(f"/observations/{obs_data['id']}/structure-confirm", json=confirm_payload)
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["status"] == "updated"

    # Check persistence
    from app.models.models import Observation
    db_obs = db.query(Observation).filter(Observation.id == uuid.UUID(obs_data["id"])).first()
    assert db_obs.structured_body == "Child asks for the toy clearly."
    assert db_obs.structuring_status == "approved"


def test_timeline_insights_recommendations(client, db):
    # Get or create parent & child
    parent = db.query(Parent).order_by(Parent.created_at.desc()).first()
    if not parent:
        parent = Parent(
            first_name="Test",
            last_name="Parent",
            email="test.parent.timeline@example.com"
        )
        db.add(parent)
        db.commit()
        db.refresh(parent)

    child = Child(
        first_name="Leo",
        last_name="Carter",
        date_of_birth=datetime.utcnow().date() - timedelta(days=730),
        gender="Male"
    )
    db.add(child)
    db.commit()
    db.refresh(child)

    # Link parent and child
    from app.models.models import parent_child_links
    db.execute(
        parent_child_links.insert().values(
            parent_id=parent.id,
            child_id=child.id,
            relationship_type="parent"
        )
    )
    db.commit()

    # Create 3 similar observations to trigger clustering!
    from app.models.models import Observation, DevelopmentalDomain
    domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.name == "Communication").first()
    
    # Let's seed observations with embedding vectors
    from app.services.ai_service import ai_engine
    vec = ai_engine.model.encode("Child asks for milk cup").tolist()
    
    for i in range(3):
        obs = Observation(
            child_id=child.id,
            parent_id=parent.id,
            body=f"Observation {i}: Child wants a toy/cup and points to ask for help.",
            entry_type="general",
            domain_id=domain.id if domain else None,
            observed_at=datetime.utcnow() - timedelta(days=i),
            embedding_vector=vec
        )
        db.add(obs)
    db.commit()

    # 1. Test timeline endpoint
    time_resp = client.get(f"/timeline/{child.id}")
    assert time_resp.status_code == 200
    time_data = time_resp.json()
    assert "grouped_observations" in time_data
    assert "clusters" in time_data
    assert len(time_data["clusters"]) >= 1

    # 2. Test insights trends endpoint
    trends_resp = client.get(f"/insights/{child.id}/trends")
    assert trends_resp.status_code == 200
    trends_data = trends_resp.json()
    assert "trends" in trends_data
    assert len(trends_data["trends"]) > 0

    # 3. Test insights changes endpoint
    changes_resp = client.get(f"/insights/{child.id}/changes")
    assert changes_resp.status_code == 200
    changes_data = changes_resp.json()
    assert "changes" in changes_data
    assert len(changes_data["changes"]) > 0

    # 4. Test recommendations endpoint
    rec_resp = client.get(f"/recommendations/{child.id}")
    assert rec_resp.status_code == 200
    rec_data = rec_resp.json()
    assert "recommendation_text" in rec_data
    assert "domain_name" in rec_data


def test_longitudinal_intelligence_features(client, db):
    # 1. Setup a parent and child
    parent = db.query(Parent).order_by(Parent.created_at.desc()).first()
    if not parent:
        parent = Parent(
            first_name="Longitudinal",
            last_name="Tester",
            email="longitudinal@example.com"
        )
        db.add(parent)
        db.commit()
        db.refresh(parent)

    child = Child(
        first_name="Sasha",
        last_name="Grey",
        date_of_birth=datetime.utcnow().date() - timedelta(days=730),
        gender="Female"
    )
    db.add(child)
    db.commit()
    db.refresh(child)

    # Link parent and child
    from app.models.models import parent_child_links
    db.execute(
        parent_child_links.insert().values(
            parent_id=parent.id,
            child_id=child.id,
            relationship_type="parent"
        )
    )
    db.commit()

    # 2. Test concern thread creation and reuse (detect_recurrence)
    # Let's log concern 1
    obs_1 = {
        "parent_id": str(parent.id),
        "body": "Rohan gets frustrated when trying to communicate.",
        "entry_type": "concern",
        "observed_at": (datetime.utcnow() - timedelta(days=20)).isoformat()
    }
    resp1 = client.post(f"/children/{child.id}/observations", json=obs_1)
    assert resp1.status_code == 201
    data1 = resp1.json()
    assert data1["recurrence_group_id"] is None  # first concern in group, no match

    # Let's log concern 2 (similar concern, but only 1 day later -> should NOT match because of < 14 days rule)
    obs_2 = {
        "parent_id": str(parent.id),
        "body": "Rohan gets frustrated because he cannot communicate.",
        "entry_type": "concern",
        "observed_at": (datetime.utcnow() - timedelta(days=19)).isoformat()
    }
    resp2 = client.post(f"/children/{child.id}/observations", json=obs_2)
    assert resp2.status_code == 201
    data2 = resp2.json()
    assert data2["recurrence_group_id"] is None  # no match, < 14 days difference

    # Let's log concern 3 (similar concern, 15 days later -> should MATCH concern 1!)
    obs_3 = {
        "parent_id": str(parent.id),
        "body": "Rohan continues to get frustrated when trying to communicate.",
        "entry_type": "concern",
        "observed_at": (datetime.utcnow() - timedelta(days=5)).isoformat()
    }
    resp3 = client.post(f"/children/{child.id}/observations", json=obs_3)
    assert resp3.status_code == 201
    data3 = resp3.json()
    assert data3["recurrence_group_id"] is not None
    group_id = data3["recurrence_group_id"]

    # Verify that the first concern also got the same recurrence_group_id
    from app.models.models import Observation
    db_obs1 = db.query(Observation).filter(Observation.id == uuid.UUID(data1["id"])).first()
    assert str(db_obs1.recurrence_group_id) == group_id

    # 3. Verify Quality Index classification (Sparse since we only have 3 observations)
    from app.services.report_service import calculate_observation_quality
    active_obs = db.query(Observation).filter(Observation.child_id == child.id).all()
    quality = calculate_observation_quality(active_obs)
    assert quality["quality_level"] == "Sparse"
    assert quality["total_observations"] == 3

    # 4. Generate first report context
    report_resp1 = client.post("/reports", json={"child_id": str(child.id)})
    assert report_resp1.status_code == 201
    rep_data1 = report_resp1.json()
    # No prior report exists, so visit_delta must be None
    assert rep_data1["report_json"]["clinician_brief"]["visit_delta"] is None
    assert rep_data1["report_json"]["clinician_brief"]["quality_data"]["quality_level"] == "Sparse"

    # Add a new milestone observation to check visit-to-visit delta milestone progress
    from app.models.models import DevelopmentalDomain
    domain = db.query(DevelopmentalDomain).first()
    obs_4 = {
        "parent_id": str(parent.id),
        "body": "Rohan is walking independently now.",
        "entry_type": "milestone",
        "domain_id": domain.id if domain else 1,
        "observed_at": datetime.utcnow().isoformat()
    }
    resp4 = client.post(f"/children/{child.id}/observations", json=obs_4)
    assert resp4.status_code == 201

    # Generate second report context
    report_resp2 = client.post("/reports", json={"child_id": str(child.id)})
    assert report_resp2.status_code == 201
    rep_data2 = report_resp2.json()
    
    # visit_delta must be present now!
    visit_delta = rep_data2["report_json"]["clinician_brief"]["visit_delta"]
    assert visit_delta is not None
    assert visit_delta["prior_visit_date"] is not None
    assert len(visit_delta["persistent_concerns"]) > 0


def test_phase_c_intelligence_features(client, db):
    # 1. Setup child and parent
    from app.models.models import Parent, Child
    parent = db.query(Parent).order_by(Parent.created_at.desc()).first()
    if not parent:
        parent = Parent(
            first_name="PhaseC",
            last_name="Tester",
            email="phasec.new@example.com"
        )
        db.add(parent)
        db.commit()
        db.refresh(parent)

    child = Child(
        first_name="Caleb",
        last_name="Stone",
        date_of_birth=datetime.utcnow().date() - timedelta(days=730),
        gender="Male"
    )
    db.add(child)
    db.commit()
    db.refresh(child)

    # Link parent and child
    from app.models.models import parent_child_links
    db.execute(
        parent_child_links.insert().values(
            parent_id=parent.id,
            child_id=child.id,
            relationship_type="parent"
        )
    )
    db.commit()

    # 2. Add observations for focus detection testing
    from app.models.models import Observation, ObservationType, DevelopmentalDomain
    comm_domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.name == "Communication").first()
    social_domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.name == "Social Emotional").first()
    
    obs_data = [
        ("He spoke two new words during dinner today.", comm_domain.id if comm_domain else 1),
        ("Caleb is speaking more words to communicate.", comm_domain.id if comm_domain else 1),
        ("He pointed at the sky and waved.", social_domain.id if social_domain else 4),
        ("Points and gestures are observed frequently.", social_domain.id if social_domain else 4),
    ]
    for body, dom_id in obs_data:
        o = Observation(
            child_id=child.id,
            parent_id=parent.id,
            body=body,
            entry_type=ObservationType.GENERAL,
            domain_id=dom_id,
            observed_at=datetime.utcnow()
        )
        db.add(o)
    db.commit()

    # 3. Test developmental focus API
    focus_resp = client.get(f"/insights/{child.id}/developmental-focus")
    assert focus_resp.status_code == 200
    focus_data = focus_resp.json()
    themes = [f["theme"] for f in focus_data["focus"]]
    assert "communication" in themes
    assert "gestures" in themes

    # 4. Test blind spots API
    bs_resp = client.get(f"/insights/{child.id}/blind-spots")
    assert bs_resp.status_code == 200
    bs_data = bs_resp.json()
    blind_spot_domains = [b["domain_name"] for b in bs_data["blind_spots"]]
    assert "Gross Motor" in blind_spot_domains
    assert len(bs_data["blind_spots"][0]["prompts"]) > 0

    # 5. Test visit prep API
    vp_resp = client.get(f"/insights/{child.id}/visit-prep")
    assert vp_resp.status_code == 200
    vp_data = vp_resp.json()
    assert "things_worth_discussing" in vp_data
    assert "recent_positive_changes" in vp_data
    assert "suggested_topics" in vp_data

    # 6. Test report parent narrative uses generate_parent_narrative
    rep_resp = client.post("/reports", json={"child_id": str(child.id)})
    assert rep_resp.status_code == 201
    rep_data = rep_resp.json()
    narrative = rep_data["report_json"]["parent_summary"]["narrative"]
    assert "Caleb" in narrative
    assert "observations" in narrative or "logging" in narrative or "logs" in narrative
