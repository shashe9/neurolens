from app.services.pattern_service import ObservationPatternExtractor

def test_pattern_extraction_pointing():
    text = "Timmy pointed to a red bird in the garden."
    patterns, cues, keywords = ObservationPatternExtractor.extract(text)
    assert "pointing" in patterns
    assert "Observation matches hand pointing behaviour." in cues
    assert "pointing" in keywords

def test_pattern_extraction_block_stacking_with_overlap():
    text = "He stacked three Lego blocks on top of the tower."
    milestone_title = "Stacks at least 4 blocks"
    patterns, cues, keywords = ObservationPatternExtractor.extract(text, milestone_title)
    assert "stacking_blocks" in patterns
    # Overlap validation
    assert any("Matches keyword: 'blocks'" in cue for cue in cues) or any("Matches keyword: 'stacked'" in cue for cue in cues)
    assert "blocks" in keywords or "stacked" in keywords

def test_pattern_extraction_multiple():
    text = "Johnny pointed to the book and said 'book'."
    patterns, cues, keywords = ObservationPatternExtractor.extract(text)
    assert "pointing" in patterns
    assert "labeling_objects" in patterns
    assert len(patterns) == 2
