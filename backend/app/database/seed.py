import json
from datetime import datetime, date
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
    ObservationType
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

    # 3. Seed Demo Parent and Child (Using Generic "Sample Child" for PR safety)
    db_parent = db.query(Parent).filter(Parent.email == "jane.doe@example.com").first()
    if not db_parent:
        db_parent = Parent(
            first_name="Jane",
            last_name="Doe",
            email="jane.doe@example.com"
        )
        db.add(db_parent)
        db.commit()
        db.refresh(db_parent)
        print("Seeded parent: Jane Doe")
    else:
        print("Parent Jane Doe already exists.")

    db_child = db.query(Child).filter(Child.first_name == "Sample", Child.last_name == "Child").first()
    if not db_child:
        db_child = Child(
            first_name="Sample",
            last_name="Child",
            date_of_birth=date(2024, 6, 15), # ~24 months as of June 2026
            gender="Female"
        )
        db.add(db_child)
        db.commit()
        db.refresh(db_child)
        print("Seeded child: Sample Child")

        # Link parent to child
        db.execute(
            parent_child_links.insert().values(
                parent_id=db_parent.id,
                child_id=db_child.id,
                relationship_type="Mother"
            )
        )
        db.commit()
        print("Linked Jane Doe to Sample Child")
    else:
        print("Child Sample Child already exists.")

    # 4. Seed qualitative observations for the Sample Child
    # Only seed if no observations exist for this child
    obs_count = db.query(Observation).filter(Observation.child_id == db_child.id).count()
    if obs_count == 0:
        comm_domain = domains_map.get("Communication")
        se_domain = domains_map.get("Social Emotional")
        
        # Query a milestone to link
        milestone = db.query(Milestone).filter(Milestone.title.like("%Points to show%")).first()

        # Obs 1: Communication Concern
        obs1 = Observation(
            child_id=db_child.id,
            parent_id=db_parent.id,
            body="Not responding when her name is called in a busy living room. Fully locked on stacking wooden rings.",
            entry_type=ObservationType.CONCERN,
            domain_id=comm_domain.id if comm_domain else None,
            observed_at=datetime(2026, 6, 10, 10, 15),
            location="Living Room",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs1)

        # Obs 2: Social Observation
        obs2 = Observation(
            child_id=db_child.id,
            parent_id=db_parent.id,
            body="Maintained continuous eye contact for several seconds when we sang the alphabet song together.",
            entry_type=ObservationType.GENERAL,
            domain_id=se_domain.id if se_domain else None,
            observed_at=datetime(2026, 6, 9, 16, 30),
            location="Playroom",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs2)

        # Obs 3: Milestone Observation
        obs3 = Observation(
            child_id=db_child.id,
            parent_id=db_parent.id,
            body="Pointed directly to the apple on the kitchen table to indicate she wanted a snack, looking back at me.",
            entry_type=ObservationType.MILESTONE,
            domain_id=comm_domain.id if comm_domain else None,
            milestone_id=milestone.id if milestone else None,
            observed_at=datetime(2026, 6, 8, 12, 0),
            location="Kitchen",
            observer_relation="Mother",
            is_regression=False
        )
        db.add(obs3)

        db.commit()
        print("Seeded 3 qualitative observations for Sample Child.")
    else:
        print("Observations for Sample Child already exist.")
        
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
