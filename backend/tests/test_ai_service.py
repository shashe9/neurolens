import numpy as np
from app.services.ai_service import ai_engine

def test_ai_engine_initialization_and_cache(db):
    # Initialize cache (it should load the 80 seeded milestones from setup_db fixture)
    ai_engine.initialize_cache(db)
    
    assert len(ai_engine.milestone_ids) == 80
    assert ai_engine.milestone_vectors.shape == (80, 384)
    # Check that metadata exists
    first_id = ai_engine.milestone_ids[0]
    assert first_id in ai_engine.milestone_metadata
    assert ai_engine.milestone_metadata[first_id]["title"] is not None

def test_ai_engine_age_decay_weighting():
    # Child is 20 months (inside milestone age range 18-24)
    w_appropriate = ai_engine.calculate_age_weight(20, 18, 24)
    assert w_appropriate == 1.0

    # Child is 30 months (older than milestone 18-24 -> developmental delay mapping)
    w_older = ai_engine.calculate_age_weight(30, 18, 24)
    assert 0.4 <= w_older < 1.0
    # Confirm decay is calculated: 1.0 - 0.05 * (30 - 24) = 1.0 - 0.30 = 0.70
    assert abs(w_older - 0.70) < 1e-5

    # Child is 12 months (younger than milestone 18-24 -> advanced milestone mapping)
    w_younger = ai_engine.calculate_age_weight(12, 18, 24)
    assert 0.1 <= w_younger < 1.0
    # Confirm decay: 1.0 - 0.15 * (18 - 12) = 1.0 - 0.90 = 0.10
    assert abs(w_younger - 0.10) < 1e-5

def test_ai_engine_retrieval(db):
    ai_engine.initialize_cache(db)
    
    # Text matches "pointing" milestone
    text = "Points to ask for something."
    obs_vector = ai_engine.model.encode(text, convert_to_numpy=True)
    obs_vector /= np.linalg.norm(obs_vector)

    # Retrieval for child aged 18 months
    suggestions = ai_engine.retrieve_milestones(obs_vector, 18, threshold=0.40)
    assert len(suggestions) > 0
    # The top suggestion should be the "Points to show someone what he wants" milestone
    top_suggestion = suggestions[0]
    assert "Points" in top_suggestion["title"] or "points" in top_suggestion["title"].lower()
    assert top_suggestion["relevance_label"] in ["Strong relevance", "Moderate relevance", "Possible relevance"]

def test_ai_engine_domain_retrieval(db):
    ai_engine.initialize_cache(db)
    
    text = "He runs easily without falling in the garden."
    obs_vector = ai_engine.model.encode(text, convert_to_numpy=True)
    obs_vector /= np.linalg.norm(obs_vector)

    domains = ai_engine.retrieve_domains(obs_vector, 18)
    assert len(domains) > 0
    # Top domain should be "Gross Motor"
    assert domains[0]["domain_name"] == "Gross Motor"

def test_ai_engine_no_match_mode(db):
    ai_engine.initialize_cache(db)
    
    # High-noise text with zero developmental relevance
    text = "The sky is blue and the weather is cloudy today."
    obs_vector = ai_engine.model.encode(text, convert_to_numpy=True)
    obs_vector /= np.linalg.norm(obs_vector)

    # Retrieval with high threshold
    suggestions = ai_engine.retrieve_milestones(obs_vector, 18, threshold=0.65)
    assert len(suggestions) == 0


def test_ai_engine_preprocess_hinglish():
    # 1. Glossary translation works
    res1 = ai_engine.preprocess_text("aankh aur kaan")
    assert "eye" in res1.lower()
    assert "ear" in res1.lower()

    # 2. Punctuation does not block translation
    res2 = ai_engine.preprocess_text("seedhiyon,")
    assert "stairs" in res2.lower()
    res2_2 = ai_engine.preprocess_text("Adults ki tarah seedhiyon par chadha.")
    assert "stairs" in res2_2.lower()
    assert "climbed" in res2_2.lower()

    # 3. Untranslated English remains unchanged
    res3 = ai_engine.preprocess_text("He runs easily without falling down.")
    assert "runs" in res3.lower()
    assert "easily" in res3.lower()
    assert "without" in res3.lower()
    assert "falling" in res3.lower()

    # 4. Mixed Hinglish/English observations are handled correctly
    res4 = ai_engine.preprocess_text("Aankh aur kaan poochne par touch karta hai.")
    assert "eye" in res4.lower()
    assert "ear" in res4.lower()
    assert "touch" in res4.lower()
