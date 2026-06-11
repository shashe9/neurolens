import json
import os
from pathlib import Path
from sqlalchemy.orm import Session
from app.database.session import SessionLocal, engine
from app.models.models import DevelopmentalDomain, EvidenceSource, Milestone

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
                
            # Check if milestone already exists
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
                
                # Link source to milestone if not already linked
                if db_source not in db_milestone.sources:
                    db_milestone.sources.append(db_source)
                    db.commit()
                    print(f"Linked evidence '{db_source.title}' to milestone '{db_milestone.title}'")
    else:
        print("No milestones.json found in database folder. Skipping milestone seed.")
        
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
