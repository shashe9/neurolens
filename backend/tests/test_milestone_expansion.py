import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.models import Milestone, DevelopmentalDomain, EvidenceSource

def test_milestone_database_count(db: Session):
    # 1. Assert total milestone count is exactly 80
    count = db.query(Milestone).count()
    assert count == 80, f"Expected 80 milestones in the database, found {count}"

def test_behavioral_patterns_absent(db: Session):
    # 2. Assert "Behavioral Patterns" domain is completely absent
    bp_domain = db.query(DevelopmentalDomain).filter(DevelopmentalDomain.name == "Behavioral Patterns").first()
    assert bp_domain is None, "Behavioral Patterns domain should be absent from the database"

def test_domains_and_age_bands_coverage(db: Session):
    # 3. Validate 5 domains and 5 age bands are fully populated
    expected_domains = ["Communication", "Gross Motor", "Fine Motor", "Social Emotional", "Cognitive"]
    
    # Check domains
    domains = db.query(DevelopmentalDomain).all()
    domain_names = [d.name for d in domains]
    assert set(domain_names) == set(expected_domains), f"Expected domains: {expected_domains}, found: {domain_names}"
    
    # Verify each domain has milestones
    for domain in domains:
        m_count = db.query(Milestone).filter(Milestone.domain_id == domain.id).count()
        assert m_count > 0, f"Domain {domain.name} has no milestones seeded"

    # Check age bands
    # The five bands are: 12-18, 18-24, 24-36, 36-48, 48-72
    expected_age_bands = [
        (12, 18),
        (18, 24),
        (24, 36),
        (36, 48),
        (48, 72)
    ]
    for low, high in expected_age_bands:
        m_count = db.query(Milestone).filter(
            Milestone.age_range_low == low,
            Milestone.age_range_high == high
        ).count()
        assert m_count > 0, f"Age band {low}-{high} months has no milestones seeded"

def test_milestones_metadata_in_json():
    # 4. Verify keyword inclusion, source metadata (with years), and example observations inside milestones.json
    json_path = Path(__file__).resolve().parent.parent / "app" / "database" / "milestones.json"
    assert json_path.exists(), "milestones.json does not exist"
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert len(data) == 80, f"Expected exactly 80 milestones in milestones.json, found {len(data)}"
    
    for idx, item in enumerate(data):
        title = item.get("title", f"Milestone at index {idx}")
        # Verify keywords exist and has 5-10 keywords
        keywords = item.get("retrieval_keywords", [])
        assert len(keywords) >= 5, f"Milestone '{title}' has less than 5 keywords"
        
        # Verify example observations exist and has 3 examples
        examples = item.get("example_observations", [])
        assert len(examples) == 3, f"Milestone '{title}' does not have exactly 3 example observations"
        
        # Verify source metadata exists with a valid year
        sources = item.get("sources", [])
        assert len(sources) > 0, f"Milestone '{title}' has no sources"
        for src in sources:
            assert "organization" in src, f"Milestone '{title}' source is missing organization"
            assert "title" in src, f"Milestone '{title}' source is missing title"
            assert "year" in src, f"Milestone '{title}' source is missing year"
            assert isinstance(src["year"], int), f"Milestone '{title}' source year must be an integer"

def test_database_descriptions_contain_keywords(db: Session):
    # Verify keyword inclusion in description inside DB
    milestones = db.query(Milestone).all()
    for m in milestones:
        assert "Keywords: " in m.description, f"Milestone description for '{m.title}' does not contain appended keywords"

def test_evaluation_dataset_file():
    # 5. Validate evaluation dataset (160 observations loaded from file)
    json_path = Path(__file__).resolve().parent.parent / "app" / "database" / "evaluation_seed_dataset.json"
    assert json_path.exists(), "evaluation_seed_dataset.json does not exist"
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert len(data) == 160, f"Expected exactly 160 observations in evaluation_seed_dataset.json, found {len(data)}"
    
    for idx, item in enumerate(data):
        assert "observation_text" in item, f"Item at index {idx} missing observation_text"
        assert "ground_truth_domain" in item, f"Item at index {idx} missing ground_truth_domain"
        assert "ground_truth_milestone_title" in item, f"Item at index {idx} missing ground_truth_milestone_title"
        
        assert item["observation_text"].strip(), f"Item at index {idx} has empty observation_text"
        assert item["ground_truth_domain"] in ["Communication", "Gross Motor", "Fine Motor", "Social Emotional", "Cognitive"], f"Item at index {idx} has invalid ground_truth_domain"
        assert item["ground_truth_milestone_title"].strip(), f"Item at index {idx} has empty ground_truth_milestone_title"

def test_evaluation_report_exists():
    report_path = Path(__file__).resolve().parent.parent / "evaluation_report.md"
    assert report_path.exists(), "evaluation_report.md does not exist"
    assert report_path.stat().st_size > 0, "evaluation_report.md is empty"
