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
    ObservationMilestoneEvidence
)

# Default domain list
DEFAULT_DOMAINS = [
    "Communication",
    "Gross Motor",
    "Fine Motor",
    "Social Emotional",
    "Cognitive",
    "Behavioral Patterns"
]

def seed_db(db: Session):
    print("Starting database seeding...")
    
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
                
            db_milestone = db.query(Milestone).filter(
                Milestone.title == m_data["title"],
                Milestone.domain_id == domain.id
            ).first()
            
            if not db_milestone:
                db_milestone = Milestone(
                    title=m_data["title"],
                    description=m_data["description"],
                    domain_id=domain.id,
                    age_range_low=m_data["age_range_low"],
                    age_range_high=m_data["age_range_high"]
                )
                db.add(db_milestone)
                db.commit()
                db.refresh(db_milestone)
                print(f"Imported milestone: {db_milestone.title}")
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
            email="demo.parent@example.com"
        )
        db.add(db_parent)
        db.commit()
        db.refresh(db_parent)
        print("Seeded parent: Demo Parent")
    else:
        print("Parent Demo Parent already exists.")

    # 4. Seed Child A (Demo Child A)
    db_child_a = db.query(Child).filter(Child.first_name == "Demo Child", Child.last_name == "A").first()
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
        print("Seeded child: Demo Child A")

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
        print("Child Demo Child A already exists.")

    # 5. Seed Child B (Demo Child B)
    db_child_b = db.query(Child).filter(Child.first_name == "Demo Child", Child.last_name == "B").first()
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
        print("Seeded child: Demo Child B")

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
        print("Child Demo Child B already exists.")

    # Fetch milestone resources to pre-link
    m_points = db.query(Milestone).filter(Milestone.title.like("%Points to show%")).first()
    m_words = db.query(Milestone).filter(Milestone.title.like("%Says at least two%")).first()
    m_face = db.query(Milestone).filter(Milestone.title.like("%Looks at your face%")).first()

    # 6. Seed qualitative observations and evidence linkages for Demo Child A
    if db.query(Observation).filter(Observation.child_id == db_child_a.id).count() == 0:
        comm_domain = domains_map.get("Communication")
        se_domain = domains_map.get("Social Emotional")

        # Observation A1: Communication Milestone (Supported)
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

        # Observation A2: Communication Milestone (Supporting the same milestone)
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

        # Link both observations to 'Points to show' milestone
        if m_points:
            db.add(ObservationMilestoneEvidence(observation_id=obs_a1.id, milestone_id=m_points.id))
            db.add(ObservationMilestoneEvidence(observation_id=obs_a2.id, milestone_id=m_points.id))
            
            # Seed Milestone Status: observed
            db.add(MilestoneStatus(
                child_id=db_child_a.id,
                milestone_id=m_points.id,
                status="observed",
                observed_date=date(2026, 6, 9),
                notes="Consistently points to request snacks or highlight objects."
            ))
            print("Linked A1 & A2 to 'Points to show' milestone and set status.")

        # Observation A3: Communication Milestone (Says at least two words together)
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
            print("Linked A3 to 'Says two words' milestone and set status.")

        # Observation A4: General social eye contact
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
        print("Seeded qualitative observations & evidence context for Demo Child A.")

    # 7. Seed qualitative observations and evidence linkages for Demo Child B
    if db.query(Observation).filter(Observation.child_id == db_child_b.id).count() == 0:
        comm_domain = domains_map.get("Communication")
        se_domain = domains_map.get("Social Emotional")

        # Observation B1: General
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

        # Observation B2: Concern
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
        print("Seeded qualitative observations for Demo Child B.")

    print("Database seeding completed successfully!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
