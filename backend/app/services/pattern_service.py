import re
from typing import Dict, List, Tuple

OBSERVATION_PATTERNS = {
    "pointing": {
        "regex": [r"point(s|ed|ing)?"],
        "cue": "Observation matches hand pointing behaviour.",
        "keyword": "pointing"
    },
    "gesturing": {
        "regex": [r"gestur(e|es|ed|ing)?", r"wav(e|es|ed|ing)?", r"nod(s|ded|ding)?", r"shak(e|es|ing)? head"],
        "cue": "Observation includes non-verbal communication gestures.",
        "keyword": "gestures"
    },
    "shared_attention": {
        "regex": [r"look(s|ed|ing)? at (my face|me)", r"gaze(s|d|ing)?", r"eye contact", r"shared attention", r"smil(ed|ing)? back"],
        "cue": "Observation demonstrates shared attention or facial referencing.",
        "keyword": "shared_attention"
    },
    "pretend_play": {
        "regex": [r"pretend(s|ed|ing)?", r"make-believe", r"feed(s|ing)? (the doll|toy)", r"toy phone"],
        "cue": "Observation contains imaginative or symbolic play patterns.",
        "keyword": "imaginative_play"
    },
    "scribbling": {
        "regex": [r"scribbl(e|es|ed|ing)?", r"draw(s|ing|n)?", r"crayon(s)?", r"marker(s)?"],
        "cue": "Observation involves fine-motor marker or crayon interaction.",
        "keyword": "fine_motor_scribbling"
    },
    "stacking_blocks": {
        "regex": [r"stack(s|ed|ing)?", r"tower", r"block(s)?", r"lego(s)?"],
        "cue": "Observation involves building or block coordination.",
        "keyword": "fine_motor_stacking"
    },
    "running": {
        "regex": [r"run(s|ning|ned)?", r"ran"],
        "cue": "Observation captures active running gross-motor activity.",
        "keyword": "gross_motor_running"
    },
    "jumping": {
        "regex": [r"jump(s|ed|ing)?", r"hop(s|ped|ping)?"],
        "cue": "Observation matches jumping or leg gross-motor coordination.",
        "keyword": "gross_motor_jumping"
    },
    "labeling_objects": {
        "regex": [r"said", r"spok(e|en)?", r"call(ed)?", r"word(s)?", r"nam(e|ed|ing)?"],
        "cue": "Observation contains object-naming or vocal labeling.",
        "keyword": "expressive_vocalization"
    }
}

class ObservationPatternExtractor:
    @staticmethod
    def extract(text: str, milestone_title: str = "") -> Tuple[List[str], List[str], List[str]]:
        """
        Parses text for observation patterns and returns matched patterns,
        explanation cues, and report keywords.
        """
        text_lower = text.lower()
        matched_patterns = []
        cues = []
        report_keywords = []

        for name, config in OBSERVATION_PATTERNS.items():
            if any(re.search(pat, text_lower) for pat in config["regex"]):
                matched_patterns.append(name)
                cues.append(config["cue"])
                report_keywords.append(config["keyword"])

        # Milestone keyword overlap explainability
        if milestone_title:
            stop_words = {"the", "and", "a", "of", "to", "in", "is", "that", "it", "he", "she", "his", "her", "with", "on", "him", "them", "at"}
            words_obs = set(re.findall(r"\w+", text_lower)) - stop_words
            words_milestone = set(re.findall(r"\w+", milestone_title.lower())) - stop_words
            overlap = words_obs.intersection(words_milestone)
            
            for word in overlap:
                cues.append(f"Matches keyword: '{word}'.")
                report_keywords.append(word)

        return list(set(matched_patterns)), list(set(cues)), list(set(report_keywords))
