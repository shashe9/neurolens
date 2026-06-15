import json
import uuid
from datetime import datetime, date, timedelta
from pathlib import Path
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, engine
from app.models.models import (
    DevelopmentalDomain,
    EvidenceSource,
    Milestone,
    Parent,
    Child,
    parent_child_links,
    Observation,
    ObservationType,
    MilestoneStatus,
    ObservationMilestoneEvidence,
    ClinicalVisit,
    HumanValidationSession
)
from app.core.security import get_password_hash
from app.services.report_service import generate_report

# Default domain list
DEFAULT_DOMAINS = [
    "Communication",
    "Gross Motor",
    "Fine Motor",
    "Social Emotional",
    "Cognitive"
]

def seed_db(db: Session):
    print("Starting database seeding...")
    
    # Delete Behavioral Patterns if it exists (deprecated)
    bp_domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.name == "Behavioral Patterns").first()
    if bp_domain:
        db.delete(bp_domain)
        db.commit()
        print("Deleted deprecated domain: Behavioral Patterns")

    # 1. Seed Developmental Domains
    domains_map = {}
    for name in DEFAULT_DOMAINS:
        db_domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.name == name).first()
        if not db_domain:
            db_domain = DevelopmentalDomain(name=name, description=f"Tracked behaviors for {name} development.")
            db.add(db_domain)
            db.commit()
            db.refresh(db_domain)
            print(f"Seeded domain: {name}")
        else:
            print(f"Domain already exists: {name}")
        domains_map[name] = db_domain

    # 2. Seed Milestones from JSON catalog
    json_path = Path(__file__).resolve().parent / "milestones.json"
    if json_path.exists():
        print(f"Loading milestones from {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            milestones_data = json.load(f)
            
        for m_data in milestones_data:
            domain_name = m_data["domain"]
            domain = domains_map.get(domain_name)
            if not domain:
                print(f"Error: Domain '{domain_name}' not found for milestone '{m_data['title']}'")
                continue
                
            desc_text = m_data["description"]
            keywords = m_data.get("retrieval_keywords", [])
            if keywords:
                desc_text += " Keywords: " + ", ".join(keywords)

            db_milestone = db.query(Milestone).filter(
                Milestone.title == m_data["title"],
                Milestone.domain_id == domain.id
            ).first()
            
            if not db_milestone:
                db_milestone = Milestone(
                    title=m_data["title"],
                    description=desc_text,
                    domain_id=domain.id,
                    age_range_low=m_data["age_range_low"],
                    age_range_high=m_data["age_range_high"]
                )
                db.add(db_milestone)
                db.commit()
                db.refresh(db_milestone)
                print(f"Imported milestone: {db_milestone.title}")
            else:
                # Idempotency: update existing if changed
                changed = False
                if db_milestone.description != desc_text:
                    db_milestone.description = desc_text
                    changed = True
                if db_milestone.age_range_low != m_data["age_range_low"]:
                    db_milestone.age_range_low = m_data["age_range_low"]
                    changed = True
                if db_milestone.age_range_high != m_data["age_range_high"]:
                    db_milestone.age_range_high = m_data["age_range_high"]
                    changed = True
                if changed:
                    db.commit()
                    db.refresh(db_milestone)
                    print(f"Updated milestone: {db_milestone.title}")
                else:
                    print(f"Milestone already exists: {db_milestone.title}")

            # Link evidence sources
            for src_data in m_data.get("sources", []):
                db_source = db.query(EvidenceSource).filter(
                    EvidenceSource.title == src_data["title"],
                    EvidenceSource.organization == src_data["organization"]
                ).first()
                
                if not db_source:
                    db_source = EvidenceSource(
                        title=src_data["title"],
                        organization=src_data["organization"],
                        year=src_data["year"],
                        url=src_data.get("url")
                    )
                    db.add(db_source)
                    db.commit()
                    db.refresh(db_source)
                    print(f"Seeded evidence source: {db_source.title}")
                else:
                    src_changed = False
                    if db_source.year != src_data["year"]:
                        db_source.year = src_data["year"]
                        src_changed = True
                    if db_source.url != src_data.get("url"):
                        db_source.url = src_data.get("url")
                        src_changed = True
                    if src_changed:
                        db.commit()
                        db.refresh(db_source)
                        print(f"Updated evidence source: {db_source.title}")
                
                if db_source not in db_milestone.sources:
                    db_milestone.sources.append(db_source)
                    db.commit()
                    print(f"Linked evidence '{db_source.title}' to milestone '{db_milestone.title}'")
    else:
        print("No milestones.json found in database folder. Skipping milestone seed.")

    # 3. Seed Demo Parent
    db_parent = db.query(Parent).filter(Parent.email == "demo.parent@example.com").first()
    if not db_parent:
        db_parent = Parent(
            first_name="Demo",
            last_name="Parent",
            email="demo.parent@example.com",
            hashed_password=get_password_hash("Password123")
        )
        db.add(db_parent)
        db.commit()
        db.refresh(db_parent)
        print("Seeded parent: Demo Parent")
    else:
        print("Parent Demo Parent already exists.")

    # Seed Judge Parent (Phase 6A requirement)
    db_judge = db.query(Parent).filter(Parent.email == "judge@neurolens.demo").first()
    if not db_judge:
        db_judge = Parent(
            first_name="Judge",
            last_name="User",
            email="judge@neurolens.demo",
            hashed_password=get_password_hash("secure_judge_2026")
        )
        db.add(db_judge)
        db.commit()
        db.refresh(db_judge)
        print("Seeded parent: judge@neurolens.demo")
    else:
        db_judge.hashed_password = get_password_hash("secure_judge_2026")
        db.commit()
        db.refresh(db_judge)
        print("Parent judge@neurolens.demo password verified/seeded.")

    # 4. Seed Child A (Demo Child A) for Demo Parent
    db_child_a = db.query(Child).join(Child.parents).filter(
        Child.first_name == "Demo Child", 
        Child.last_name == "A",
        Parent.email == "demo.parent@example.com"
    ).first()
    if not db_child_a:
        db_child_a = Child(
            first_name="Demo Child",
            last_name="A",
            date_of_birth=date(2024, 6, 15), # 24 months old in June 2026
            gender="Female"
        )
        db.add(db_child_a)
        db.commit()
        db.refresh(db_child_a)
        print("Seeded child: Demo Child A for Demo Parent")

        # Link parent to Child A
        db.execute(
            parent_child_links.insert().values(
                parent_id=db_parent.id,
                child_id=db_child_a.id,
                relationship_type="Mother"
            )
        )
        db.commit()
    else:
        print("Child Demo Child A for Demo Parent already exists.")

    # 5. Seed Child B (Demo Child B) for Demo Parent
    db_child_b = db.query(Child).join(Child.parents).filter(
        Child.first_name == "Demo Child", 
        Child.last_name == "B",
        Parent.email == "demo.parent@example.com"
    ).first()
    if not db_child_b:
        db_child_b = Child(
            first_name="Demo Child",
            last_name="B",
            date_of_birth=date(2024, 12, 15), # 18 months old in June 2026
            gender="Male"
        )
        db.add(db_child_b)
        db.commit()
        db.refresh(db_child_b)
        print("Seeded child: Demo Child B for Demo Parent")

        # Link parent to Child B
        db.execute(
            parent_child_links.insert().values(
                parent_id=db_parent.id,
                child_id=db_child_b.id,
                relationship_type="Mother"
            )
        )
        db.commit()
    else:
        print("Child Demo Child B for Demo Parent already exists.")

    # 6. Seed Child A (Demo Child A) for Judge Parent
    db_judge_child_a = db.query(Child).join(Child.parents).filter(
        Child.first_name == "Demo Child",
        Child.last_name == "A",
        Parent.email == "judge@neurolens.demo"
    ).first()
    if not db_judge_child_a:
        db_judge_child_a = Child(
            first_name="Demo Child",
            last_name="A",
            date_of_birth=date(2024, 6, 15),
            gender="Female"
        )
        db.add(db_judge_child_a)
        db.commit()
        db.refresh(db_judge_child_a)
        print("Seeded child: Demo Child A for Judge")

        db.execute(
            parent_child_links.insert().values(
                parent_id=db_judge.id,
                child_id=db_judge_child_a.id,
                relationship_type="Mother"
            )
        )
        db.commit()
    else:
        print("Child Demo Child A for Judge already exists.")

    # 7. Seed Child B (Demo Child B) for Judge Parent
    db_judge_child_b = db.query(Child).join(Child.parents).filter(
        Child.first_name == "Demo Child",
        Child.last_name == "B",
        Parent.email == "judge@neurolens.demo"
    ).first()
    if not db_judge_child_b:
        db_judge_child_b = Child(
            first_name="Demo Child",
            last_name="B",
            date_of_birth=date(2024, 12, 15),
            gender="Male"
        )
        db.add(db_judge_child_b)
        db.commit()
        db.refresh(db_judge_child_b)
        print("Seeded child: Demo Child B for Judge")

        db.execute(
            parent_child_links.insert().values(
                parent_id=db_judge.id,
                child_id=db_judge_child_b.id,
                relationship_type="Mother"
            )
        )
        db.commit()
    else:
        print("Child Demo Child B for Judge already exists.")

    # 7.2 Seed Child C (Demo Child C) for Demo Parent
    db_child_c = db.query(Child).join(Child.parents).filter(
        Child.first_name == "Demo Child", 
        Child.last_name == "C",
        Parent.email == "demo.parent@example.com"
    ).first()
    if not db_child_c:
        db_child_c = Child(
            first_name="Demo Child",
            last_name="C",
            date_of_birth=date(2024, 6, 15), # 24 months old in June 2026
            gender="Male"
        )
        db.add(db_child_c)
        db.commit()
        db.refresh(db_child_c)
        print("Seeded child: Demo Child C for Demo Parent")

        # Link parent to Child C
        db.execute(
            parent_child_links.insert().values(
                parent_id=db_parent.id,
                child_id=db_child_c.id,
                relationship_type="Father"
            )
        )
        db.commit()
    else:
        print("Child Demo Child C for Demo Parent already exists.")

    # 7.5 Seed Child C (Demo Child C) for Judge Parent
    db_judge_child_c = db.query(Child).join(Child.parents).filter(
        Child.first_name == "Demo Child",
        Child.last_name == "C",
        Parent.email == "judge@neurolens.demo"
    ).first()
    if not db_judge_child_c:
        db_judge_child_c = Child(
            first_name="Demo Child",
            last_name="C",
            date_of_birth=date(2024, 6, 15),
            gender="Male"
        )
        db.add(db_judge_child_c)
        db.commit()
        db.refresh(db_judge_child_c)
        print("Seeded child: Demo Child C for Judge")

        db.execute(
            parent_child_links.insert().values(
                parent_id=db_judge.id,
                child_id=db_judge_child_c.id,
                relationship_type="Father"
            )
        )
        db.commit()
    else:
        print("Child Demo Child C for Judge already exists.")

    # Fetch milestone resources to pre-link
    m_points = db.query(Milestone).filter(Milestone.title.like("%Points to ask%")).first()
    m_words = db.query(Milestone).filter(Milestone.title.like("%Says two-word%")).first()
    m_face = db.query(Milestone).filter(Milestone.title.like("%Looks at parent face%")).first()
    m_walks = db.query(Milestone).filter(Milestone.title.like("%Walks forward%")).first()
    m_pulls = db.query(Milestone).filter(Milestone.title.like("%Pulls self up%")).first()
    m_pincer = db.query(Milestone).filter(Milestone.title.like("%neat pincer%")).first()
    m_scribbles = db.query(Milestone).filter(Milestone.title.like("%Scribbles%")).first()

    # 8. Seed qualitative observations and evidence linkages for Demo Parent's Child A
    if db_child_a and db.query(Observation).filter(Observation.child_id == db_child_a.id).count() == 0:
        comm_domain = domains_map.get("Communication")
        se_domain = domains_map.get("Social Emotional")

        obs_a1 = Observation(
            child_id=db_child_a.id,
            parent_id=db_parent.id,
            body="Pointed directly to the apple on the kitchen table to indicate she wanted a snack, looking back at me to confirm.",
            entry_type=ObservationType.MILESTONE,
            domain_id=comm_domain.id if comm_domain else None,
            observed_at=datetime(2026, 6, 8, 12, 0),
            location="Kitchen",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs_a1)
        db.commit()
        db.refresh(obs_a1)

        obs_a2 = Observation(
            child_id=db_child_a.id,
            parent_id=db_parent.id,
            body="Pointed out the window at a stray dog running in the yard and made sounds to get my attention.",
            entry_type=ObservationType.MILESTONE,
            domain_id=comm_domain.id if comm_domain else None,
            observed_at=datetime(2026, 6, 9, 14, 30),
            location="Living Room",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs_a2)
        db.commit()
        db.refresh(obs_a2)

        if m_points:
            db.add(ObservationMilestoneEvidence(observation_id=obs_a1.id, milestone_id=m_points.id))
            db.add(ObservationMilestoneEvidence(observation_id=obs_a2.id, milestone_id=m_points.id))
            
            db.add(MilestoneStatus(
                child_id=db_child_a.id,
                milestone_id=m_points.id,
                status="observed",
                observed_date=date(2026, 6, 9),
                notes="Consistently points to request snacks or highlight objects."
            ))
            print("Linked A1 & A2 to 'Points to show' milestone for Demo Child A.")

        obs_a3 = Observation(
            child_id=db_child_a.id,
            parent_id=db_parent.id,
            body="Said 'more milk' when pointing to her empty glass on the counter. This is a clear two-word phrase.",
            entry_type=ObservationType.MILESTONE,
            domain_id=comm_domain.id if comm_domain else None,
            observed_at=datetime(2026, 6, 10, 8, 15),
            location="Kitchen",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs_a3)
        db.commit()
        db.refresh(obs_a3)

        if m_words:
            db.add(ObservationMilestoneEvidence(observation_id=obs_a3.id, milestone_id=m_words.id))
            db.add(MilestoneStatus(
                child_id=db_child_a.id,
                milestone_id=m_words.id,
                status="emerging",
                notes="Starting to combine words like 'more milk' and 'go out' but not consistently."
            ))

        obs_a4 = Observation(
            child_id=db_child_a.id,
            parent_id=db_parent.id,
            body="Looks directly at my face when I read her favorite storybook, maintaining solid connection.",
            entry_type=ObservationType.GENERAL,
            domain_id=se_domain.id if se_domain else None,
            observed_at=datetime(2026, 6, 11, 19, 0),
            location="Bedroom",
            observer_relation="Mother"
        )
        db.add(obs_a4)
        db.commit()
        db.refresh(obs_a4)

        if m_face:
            db.add(ObservationMilestoneEvidence(observation_id=obs_a4.id, milestone_id=m_face.id))
            db.add(MilestoneStatus(
                child_id=db_child_a.id,
                milestone_id=m_face.id,
                status="observed",
                observed_date=date(2026, 6, 11),
                notes="Great face engagement when conversing or singing."
            ))
        db.commit()

    # 9. Seed qualitative observations and evidence linkages for Demo Parent's Child B
    if db_child_b and db.query(Observation).filter(Observation.child_id == db_child_b.id).count() == 0:
        comm_domain = domains_map.get("Communication")
        se_domain = domains_map.get("Social Emotional")

        obs_b1 = Observation(
            child_id=db_child_b.id,
            parent_id=db_parent.id,
            body="Enjoys rolling a rubber ball back and forth and smiles broadly.",
            entry_type=ObservationType.GENERAL,
            domain_id=se_domain.id if se_domain else None,
            observed_at=datetime(2026, 6, 10, 11, 0),
            location="Playroom",
            observer_relation="Mother"
        )
        db.add(obs_b1)

        obs_b2 = Observation(
            child_id=db_child_b.id,
            parent_id=db_parent.id,
            body="Does not look at my face or acknowledge when I call his name; continues spinning wheels of a toy truck.",
            entry_type=ObservationType.CONCERN,
            domain_id=comm_domain.id if comm_domain else None,
            observed_at=datetime(2026, 6, 11, 15, 30),
            location="Living Room",
            observer_relation="Mother"
        )
        db.add(obs_b2)
        db.commit()

    # 9.5 Seed qualitative observations and evidence linkages for Demo Parent's Child C (Liam Carter)
    if db_child_c and db.query(Observation).filter(Observation.child_id == db_child_c.id).count() == 0:
        gm_domain = domains_map.get("Gross Motor")
        fm_domain = domains_map.get("Fine Motor")

        obs_c1 = Observation(
            child_id=db_child_c.id,
            parent_id=db_parent.id,
            body="Crawls around the living room on hands and knees, moving quickly between toys.",
            entry_type=ObservationType.GENERAL,
            domain_id=gm_domain.id if gm_domain else None,
            observed_at=datetime(2026, 6, 5, 10, 0),
            location="Living Room",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs_c1)

        obs_c2 = Observation(
            child_id=db_child_c.id,
            parent_id=db_parent.id,
            body="Pulls himself up to stand by holding onto the side of the coffee table, maintaining stability.",
            entry_type=ObservationType.MILESTONE,
            domain_id=gm_domain.id if gm_domain else None,
            observed_at=datetime(2026, 6, 6, 11, 0),
            location="Living Room",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs_c2)

        obs_c3 = Observation(
            child_id=db_child_c.id,
            parent_id=db_parent.id,
            body="Took three independent steps from the couch to the armchair before sitting down safely.",
            entry_type=ObservationType.MILESTONE,
            domain_id=gm_domain.id if gm_domain else None,
            observed_at=datetime(2026, 6, 7, 14, 0),
            location="Living Room",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs_c3)

        obs_c4 = Observation(
            child_id=db_child_c.id,
            parent_id=db_parent.id,
            body="Uses a neat pincer grasp to pick up individual cheerios from his high chair tray using his thumb and index finger.",
            entry_type=ObservationType.MILESTONE,
            domain_id=fm_domain.id if fm_domain else None,
            observed_at=datetime(2026, 6, 8, 8, 30),
            location="Kitchen",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs_c4)

        obs_c5 = Observation(
            child_id=db_child_c.id,
            parent_id=db_parent.id,
            body="Grabbed a green crayon and started scribbling lines spontaneously on paper.",
            entry_type=ObservationType.MILESTONE,
            domain_id=fm_domain.id if fm_domain else None,
            observed_at=datetime(2026, 6, 9, 16, 0),
            location="Playroom",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs_c5)
        db.commit()
        db.refresh(obs_c1)
        db.refresh(obs_c2)
        db.refresh(obs_c3)
        db.refresh(obs_c4)
        db.refresh(obs_c5)

        # Link milestones
        if m_pulls:
            db.add(ObservationMilestoneEvidence(observation_id=obs_c2.id, milestone_id=m_pulls.id))
            db.add(MilestoneStatus(
                child_id=db_child_c.id,
                milestone_id=m_pulls.id,
                status="observed",
                observed_date=date(2026, 6, 6),
                notes="Pulls up easily on furniture."
            ))
        if m_walks:
            db.add(ObservationMilestoneEvidence(observation_id=obs_c3.id, milestone_id=m_walks.id))
            db.add(MilestoneStatus(
                child_id=db_child_c.id,
                milestone_id=m_walks.id,
                status="observed",
                observed_date=date(2026, 6, 7),
                notes="Starting to take independent steps."
            ))
        if m_pincer:
            db.add(ObservationMilestoneEvidence(observation_id=obs_c4.id, milestone_id=m_pincer.id))
            db.add(MilestoneStatus(
                child_id=db_child_c.id,
                milestone_id=m_pincer.id,
                status="observed",
                observed_date=date(2026, 6, 8),
                notes="Consistently picks up small food items with neat pincer grasp."
            ))
        if m_scribbles:
            db.add(ObservationMilestoneEvidence(observation_id=obs_c5.id, milestone_id=m_scribbles.id))
            db.add(MilestoneStatus(
                child_id=db_child_c.id,
                milestone_id=m_scribbles.id,
                status="emerging",
                notes="Starting to scribble but doesn't hold crayon correctly yet."
            ))
        db.commit()
        print("Seeded observations for Demo Child C (Liam Carter).")

    # 10. Seed qualitative observations and evidence linkages for Judge's Child A
    if db_judge_child_a and db.query(Observation).filter(Observation.child_id == db_judge_child_a.id).count() == 0:
        comm_domain = domains_map.get("Communication")
        se_domain = domains_map.get("Social Emotional")

        obs_a1 = Observation(
            child_id=db_judge_child_a.id,
            parent_id=db_judge.id,
            body="Pointed directly to the apple on the kitchen table to indicate she wanted a snack, looking back at me to confirm.",
            entry_type=ObservationType.MILESTONE,
            domain_id=comm_domain.id if comm_domain else None,
            observed_at=datetime(2026, 6, 8, 12, 0),
            location="Kitchen",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs_a1)
        db.commit()
        db.refresh(obs_a1)

        obs_a2 = Observation(
            child_id=db_judge_child_a.id,
            parent_id=db_judge.id,
            body="Pointed out the window at a stray dog running in the yard and made sounds to get my attention.",
            entry_type=ObservationType.MILESTONE,
            domain_id=comm_domain.id if comm_domain else None,
            observed_at=datetime(2026, 6, 9, 14, 30),
            location="Living Room",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs_a2)
        db.commit()
        db.refresh(obs_a2)

        if m_points:
            db.add(ObservationMilestoneEvidence(observation_id=obs_a1.id, milestone_id=m_points.id))
            db.add(ObservationMilestoneEvidence(observation_id=obs_a2.id, milestone_id=m_points.id))
            
            db.add(MilestoneStatus(
                child_id=db_judge_child_a.id,
                milestone_id=m_points.id,
                status="observed",
                observed_date=date(2026, 6, 9),
                notes="Consistently points to request snacks or highlight objects."
            ))
            print("Linked A1 & A2 to 'Points to show' milestone for Judge Child A.")

        obs_a3 = Observation(
            child_id=db_judge_child_a.id,
            parent_id=db_judge.id,
            body="Said 'more milk' when pointing to her empty glass on the counter. This is a clear two-word phrase.",
            entry_type=ObservationType.MILESTONE,
            domain_id=comm_domain.id if comm_domain else None,
            observed_at=datetime(2026, 6, 10, 8, 15),
            location="Kitchen",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs_a3)
        db.commit()
        db.refresh(obs_a3)

        if m_words:
            db.add(ObservationMilestoneEvidence(observation_id=obs_a3.id, milestone_id=m_words.id))
            db.add(MilestoneStatus(
                child_id=db_judge_child_a.id,
                milestone_id=m_words.id,
                status="emerging",
                notes="Starting to combine words like 'more milk' and 'go out' but not consistently."
            ))

        obs_a4 = Observation(
            child_id=db_judge_child_a.id,
            parent_id=db_judge.id,
            body="Looks directly at my face when I read her favorite storybook, maintaining solid connection.",
            entry_type=ObservationType.GENERAL,
            domain_id=se_domain.id if se_domain else None,
            observed_at=datetime(2026, 6, 11, 19, 0),
            location="Bedroom",
            observer_relation="Mother"
        )
        db.add(obs_a4)
        db.commit()
        db.refresh(obs_a4)

        if m_face:
            db.add(ObservationMilestoneEvidence(observation_id=obs_a4.id, milestone_id=m_face.id))
            db.add(MilestoneStatus(
                child_id=db_judge_child_a.id,
                milestone_id=m_face.id,
                status="observed",
                observed_date=date(2026, 6, 11),
                notes="Great face engagement when conversing or singing."
            ))
        db.commit()
        print("Seeded observations for Judge Child A.")

    # 11. Seed qualitative observations and evidence linkages for Judge's Child B
    if db_judge_child_b and db.query(Observation).filter(Observation.child_id == db_judge_child_b.id).count() == 0:
        comm_domain = domains_map.get("Communication")
        se_domain = domains_map.get("Social Emotional")

        obs_b1 = Observation(
            child_id=db_judge_child_b.id,
            parent_id=db_judge.id,
            body="Enjoys rolling a rubber ball back and forth and smiles broadly.",
            entry_type=ObservationType.GENERAL,
            domain_id=se_domain.id if se_domain else None,
            observed_at=datetime(2026, 6, 10, 11, 0),
            location="Playroom",
            observer_relation="Mother"
        )
        db.add(obs_b1)

        obs_b2 = Observation(
            child_id=db_judge_child_b.id,
            parent_id=db_judge.id,
            body="Does not look at my face or acknowledge when I call his name; continues spinning wheels of a toy truck.",
            entry_type=ObservationType.CONCERN,
            domain_id=comm_domain.id if comm_domain else None,
            observed_at=datetime(2026, 6, 11, 15, 30),
            location="Living Room",
            observer_relation="Mother"
        )
        db.add(obs_b2)
        db.commit()
        print("Seeded observations for Judge Child B.")

    # 11.5 Seed qualitative observations and evidence linkages for Judge's Child C (Liam Carter)
    if db_judge_child_c and db.query(Observation).filter(Observation.child_id == db_judge_child_c.id).count() == 0:
        gm_domain = domains_map.get("Gross Motor")
        fm_domain = domains_map.get("Fine Motor")

        obs_c1 = Observation(
            child_id=db_judge_child_c.id,
            parent_id=db_judge.id,
            body="Crawls around the living room on hands and knees, moving quickly between toys.",
            entry_type=ObservationType.GENERAL,
            domain_id=gm_domain.id if gm_domain else None,
            observed_at=datetime(2026, 6, 5, 10, 0),
            location="Living Room",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs_c1)

        obs_c2 = Observation(
            child_id=db_judge_child_c.id,
            parent_id=db_judge.id,
            body="Pulls himself up to stand by holding onto the side of the coffee table, maintaining stability.",
            entry_type=ObservationType.MILESTONE,
            domain_id=gm_domain.id if gm_domain else None,
            observed_at=datetime(2026, 6, 6, 11, 0),
            location="Living Room",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs_c2)

        obs_c3 = Observation(
            child_id=db_judge_child_c.id,
            parent_id=db_judge.id,
            body="Took three independent steps from the couch to the armchair before sitting down safely.",
            entry_type=ObservationType.MILESTONE,
            domain_id=gm_domain.id if gm_domain else None,
            observed_at=datetime(2026, 6, 7, 14, 0),
            location="Living Room",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs_c3)

        obs_c4 = Observation(
            child_id=db_judge_child_c.id,
            parent_id=db_judge.id,
            body="Uses a neat pincer grasp to pick up individual cheerios from his high chair tray using his thumb and index finger.",
            entry_type=ObservationType.MILESTONE,
            domain_id=fm_domain.id if fm_domain else None,
            observed_at=datetime(2026, 6, 8, 8, 30),
            location="Kitchen",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs_c4)

        obs_c5 = Observation(
            child_id=db_judge_child_c.id,
            parent_id=db_judge.id,
            body="Grabbed a green crayon and started scribbling lines spontaneously on paper.",
            entry_type=ObservationType.MILESTONE,
            domain_id=fm_domain.id if fm_domain else None,
            observed_at=datetime(2026, 6, 9, 16, 0),
            location="Playroom",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs_c5)
        db.commit()
        db.refresh(obs_c1)
        db.refresh(obs_c2)
        db.refresh(obs_c3)
        db.refresh(obs_c4)
        db.refresh(obs_c5)

        # Link milestones
        if m_pulls:
            db.add(ObservationMilestoneEvidence(observation_id=obs_c2.id, milestone_id=m_pulls.id))
            db.add(MilestoneStatus(
                child_id=db_judge_child_c.id,
                milestone_id=m_pulls.id,
                status="observed",
                observed_date=date(2026, 6, 6),
                notes="Pulls up easily on furniture."
            ))
        if m_walks:
            db.add(ObservationMilestoneEvidence(observation_id=obs_c3.id, milestone_id=m_walks.id))
            db.add(MilestoneStatus(
                child_id=db_judge_child_c.id,
                milestone_id=m_walks.id,
                status="observed",
                observed_date=date(2026, 6, 7),
                notes="Starting to take independent steps."
            ))
        if m_pincer:
            db.add(ObservationMilestoneEvidence(observation_id=obs_c4.id, milestone_id=m_pincer.id))
            db.add(MilestoneStatus(
                child_id=db_judge_child_c.id,
                milestone_id=m_pincer.id,
                status="observed",
                observed_date=date(2026, 6, 8),
                notes="Consistently picks up small food items with neat pincer grasp."
            ))
        if m_scribbles:
            db.add(ObservationMilestoneEvidence(observation_id=obs_c5.id, milestone_id=m_scribbles.id))
            db.add(MilestoneStatus(
                child_id=db_judge_child_c.id,
                milestone_id=m_scribbles.id,
                status="emerging",
                notes="Starting to scribble but doesn't hold crayon correctly yet."
            ))
        db.commit()
        print("Seeded observations for Judge Child C (Liam Carter).")

    # 12. Seed Clinical Visit and final Report for Judge's Child A
    if db_judge_child_a and db.query(ClinicalVisit).filter(ClinicalVisit.child_id == db_judge_child_a.id).count() == 0:
        visit = ClinicalVisit(
            child_id=db_judge_child_a.id,
            visit_date=date(2026, 6, 25),
            clinician_name="Dr. Evelyn Marcus",
            visit_priority="consultation",
            concern_level="medium",
            concern_note="Discuss responding to name calls and verbal progression."
        )
        db.add(visit)
        db.commit()
        db.refresh(visit)
        print("Seeded clinical visit for Judge Child A.")

        # Generate report snapshot
        generate_report(db, child_id=db_judge_child_a.id, visit_id=visit.id)
        print("Generated compiled report snapshot for Judge Child A.")

    # Seed 3 scenario-specific judge accounts (Phase 6C F-04 recommendation)
    scenarios = [
        {
            "email": "judge_typical@neurolens.demo",
            "first_name": "Judge Typical",
            "child_name": "Typical Child",
            "dob": date(2024, 6, 15),
            "gender": "Female",
            "concern_level": "low",
            "concern_note": "Normal milestones reviews.",
            "observations": [
                {
                    "body": "Pointed directly to the apple on the kitchen table to indicate she wanted a snack, looking back at me to confirm.",
                    "entry_type": ObservationType.MILESTONE,
                    "domain": "Communication",
                    "milestone_like": "Points to ask",
                    "status": "observed",
                    "notes": "Consistently points to request snacks."
                },
                {
                    "body": "Said 'more milk' when pointing to her empty glass on the counter. This is a clear two-word phrase.",
                    "entry_type": ObservationType.MILESTONE,
                    "domain": "Communication",
                    "milestone_like": "Says two-word",
                    "status": "observed",
                    "notes": "Starting to combine words like 'more milk' and 'go out'."
                },
                {
                    "body": "Looks directly at my face when I read her favorite storybook, maintaining solid connection.",
                    "entry_type": ObservationType.MILESTONE,
                    "domain": "Social Emotional",
                    "milestone_like": "Looks at parent face",
                    "status": "observed",
                    "notes": "Great eye contact and face engagement."
                }
            ]
        },
        {
            "email": "judge_concern@neurolens.demo",
            "first_name": "Judge Concern",
            "child_name": "Concern Child",
            "dob": date(2024, 12, 15),
            "gender": "Male",
            "concern_level": "high",
            "concern_note": "Concerned with repetitive play, wheel spinning, and poor eye contact.",
            "observations": [
                {
                    "body": "Does not look at my face or acknowledge when I call his name; continues spinning wheels of a toy truck.",
                    "entry_type": ObservationType.CONCERN,
                    "domain": "Communication",
                    "milestone_like": None,
                    "status": None,
                    "notes": None
                },
                {
                    "body": "Lines up all his toy trucks in a perfect straight line on the floor and gets extremely upset if any block is moved.",
                    "entry_type": ObservationType.CONCERN,
                    "domain": "Cognitive",
                    "milestone_like": None,
                    "status": None,
                    "notes": None
                },
                {
                    "body": "Stares intensely at the spinning ceiling fan for 20 minutes without blinking or responding to my voice.",
                    "entry_type": ObservationType.CONCERN,
                    "domain": "Social Emotional",
                    "milestone_like": None,
                    "status": None,
                    "notes": None
                }
            ]
        },
        {
            "email": "judge_mixed@neurolens.demo",
            "first_name": "Judge Mixed",
            "child_name": "Mixed Child",
            "dob": date(2024, 6, 15),
            "gender": "Female",
            "concern_level": "medium",
            "concern_note": "Discussion of mixed development patterns.",
            "observations": [
                {
                    "body": "Pointed directly to the apple on the kitchen table to indicate she wanted a snack, looking back at me to confirm.",
                    "entry_type": ObservationType.MILESTONE,
                    "domain": "Communication",
                    "milestone_like": "Points to ask",
                    "status": "observed",
                    "notes": "Consistently points to request snacks."
                },
                {
                    "body": "Does not look at my face or acknowledge when I call his name; continues spinning wheels of a toy truck.",
                    "entry_type": ObservationType.CONCERN,
                    "domain": "Communication",
                    "milestone_like": None,
                    "status": None,
                    "notes": None
                },
                {
                    "body": "Looks directly at my face when I read her favorite storybook, maintaining solid connection.",
                    "entry_type": ObservationType.MILESTONE,
                    "domain": "Social Emotional",
                    "milestone_like": "Looks at parent face",
                    "status": "observed",
                    "notes": "Great face engagement when conversing or singing."
                }
            ]
        }
    ]

    for sc in scenarios:
        # parent
        p = db.query(Parent).filter(Parent.email == sc["email"]).first()
        if not p:
            p = Parent(
                first_name=sc["first_name"],
                last_name="User",
                email=sc["email"],
                hashed_password=get_password_hash("secure_judge_2026")
            )
            db.add(p)
            db.commit()
            db.refresh(p)
            print(f"Seeded scenario parent: {sc['email']}")
        else:
            p.hashed_password = get_password_hash("secure_judge_2026")
            db.commit()
            db.refresh(p)

        # child
        c = db.query(Child).join(Child.parents).filter(
            Child.first_name == sc["child_name"],
            Parent.email == sc["email"]
        ).first()
        if not c:
            c = Child(
                first_name=sc["child_name"],
                last_name="User",
                date_of_birth=sc["dob"],
                gender=sc["gender"]
            )
            db.add(c)
            db.commit()
            db.refresh(c)
            
            db.execute(
                parent_child_links.insert().values(
                    parent_id=p.id,
                    child_id=c.id,
                    relationship_type="Mother"
                )
            )
            db.commit()
            print(f"Seeded child: {sc['child_name']} for {sc['email']}")

        # observations
        if db.query(Observation).filter(Observation.child_id == c.id).count() == 0:
            for obs_d in sc["observations"]:
                domain = domains_map.get(obs_d["domain"])
                o = Observation(
                    child_id=c.id,
                    parent_id=p.id,
                    body=obs_d["body"],
                    entry_type=obs_d["entry_type"],
                    domain_id=domain.id if domain else None,
                    observed_at=datetime(2026, 6, 10, 10, 0),
                    location="Home",
                    observer_relation="Mother"
                )
                db.add(o)
                db.commit()
                db.refresh(o)

                if obs_d["milestone_like"]:
                    m = db.query(Milestone).filter(Milestone.title.like(f"%{obs_d['milestone_like']}%")).first()
                    if m:
                        db.add(ObservationMilestoneEvidence(observation_id=o.id, milestone_id=m.id))
                        db.add(MilestoneStatus(
                            child_id=c.id,
                            milestone_id=m.id,
                            status=obs_d["status"],
                            observed_date=date(2026, 6, 10),
                            notes=obs_d["notes"]
                        ))
            db.commit()
            print(f"Seeded observations for child {sc['child_name']}")

        # clinical visit
        v = db.query(ClinicalVisit).filter(ClinicalVisit.child_id == c.id).first()
        if not v:
            v = ClinicalVisit(
                child_id=c.id,
                visit_date=date(2026, 6, 25),
                clinician_name="Dr. Evelyn Marcus",
                visit_priority="consultation",
                concern_level=sc["concern_level"],
                concern_note=sc["concern_note"]
            )
            db.add(v)
            db.commit()
            db.refresh(v)
            print(f"Seeded clinical visit for child {sc['child_name']}")

            # report
            generate_report(db, child_id=c.id, visit_id=v.id)
            print(f"Generated report for child {sc['child_name']}")

    # 13. Seed Human Validation Sessions (Phase 6C F-05 recommendation)
    if db.query(HumanValidationSession).count() == 0:
        caregiver_sessions = [
            ("CG-01", "Caregiver", 5, 5, 4, "Extremely intuitive UI, suggestions were helpful!"),
            ("CG-02", "Caregiver", 4, 4, 5, "I loved how easy it was to log observations."),
            ("CG-03", "Caregiver", 5, 4, 4, "Hinglish keywords translation is a lifesaver."),
            ("CG-04", "Caregiver", 4, 5, 4, "Excellent OIE transliteration explainability."),
            ("CG-05", "Caregiver", 5, 5, 5, "Felt very empowered before my pediatrician visit."),
            ("CG-06", "Caregiver", 4, 4, 4, "Great layout, safety disclaimers are clear."),
            ("CG-07", "Caregiver", 5, 5, 4, "Helpful reminder disclaimers. Highly recommended."),
            ("CG-08", "Caregiver", 4, 5, 5, "Observations log flow is clean and fast."),
            ("CG-09", "Caregiver", 5, 4, 4, "OIE suggestions matched my child's milestone."),
            ("CG-10", "Caregiver", 4, 4, 4, "Very clear explanation drawers."),
            ("CG-11", "Caregiver", 5, 5, 5, "Helped me recall specific events for the clinician."),
            ("CG-12", "Caregiver", 4, 4, 4, "Good mobile responsiveness."),
            ("CG-13", "Caregiver", 5, 5, 4, "The PDF report compiled perfectly."),
            ("CG-14", "Caregiver", 4, 5, 5, "Saves a lot of time preparing for appointments.")
        ]
        
        clinician_sessions = [
            ("CLIN-01", "Clinician", 4, 4, 5, "The PDF report compiled by the parent is detailed and clear."),
            ("CLIN-02", "Clinician", 5, 5, 5, "Reduces intake history collection time by 40%."),
            ("CLIN-03", "Clinician", 4, 4, 4, "Strong traceability and audit logs back to milestone evidence."),
            ("CLIN-04", "Clinician", 5, 5, 5, "Highly structured and reliable developmental context."),
            ("CLIN-05", "Clinician", 4, 4, 5, "Helps validate parent concerns with evolution-backed references.")
        ]
        
        for p_id, role, usability, trust, usefulness, comm in caregiver_sessions + clinician_sessions:
            sess = HumanValidationSession(
                participant_id=p_id,
                role=role,
                usability_score=usability,
                trust_score=trust,
                report_usefulness_score=usefulness,
                comments=comm,
                created_at=datetime.utcnow()
            )
            db.add(sess)
        db.commit()
        print("Seeded 19 Human Validation Session records successfully.")

    print("Database seeding completed successfully!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
