import re
from typing import Any, Optional

# Re-use keywords or typical indicators of high-specificity logging
SPECIFIC_KEYWORDS = [
    # Quantitative keywords
    r"\d+\s*(of|out\s*of)\s*\d+", # e.g. "8 of 10" or "8 out of 10"
    r"\d+\s*times",               # e.g. "3 times"
    r"seconds|minutes",
    # Specific developmental terms
    r"joint attention", r"eye contact", r"pointing", r"pointed", r"waved", r"waving",
    r"responded to name", r"respond to name", r"shook head", r"nodded",
    r"two-word", r"sentence", r"phrase", r"imaginative", r"pretend",
    r"stacked", r"pincer grasp", r"scribbled", r"climb", r"crawl"
]

def calculate_single_observation_quality(
    body: str,
    location: Optional[str] = None,
    observer_relation: Optional[str] = None,
    context_note: Optional[str] = None
) -> float:
    """
    Calculates an internal quality score between 0.0 and 1.0 for a single log.
    - Length: up to 0.3
    - Context richness: up to 0.3
    - Specificity/Quantitative detail: up to 0.3
    - Base score: 0.1
    """
    if not body or not body.strip():
        return 0.0

    score = 0.1 # Base score

    # 1. Length scoring (up to 0.3)
    text_len = len(body.strip())
    if text_len > 150:
        score += 0.3
    elif text_len > 50:
        score += 0.2
    elif text_len > 20:
        score += 0.1

    # 2. Context richness (up to 0.3)
    if location and location.strip():
        score += 0.1
    if observer_relation and observer_relation.strip():
        score += 0.1
    if context_note and context_note.strip():
        score += 0.1

    # 3. Specificity & Quantitative matching (up to 0.3)
    body_lower = body.lower()
    matched_specifics = 0
    for pattern in SPECIFIC_KEYWORDS:
        if re.search(pattern, body_lower):
            matched_specifics += 1
    
    if matched_specifics >= 2:
        score += 0.3
    elif matched_specifics == 1:
        score += 0.15

    return min(1.0, max(0.0, round(score, 2)))
