import re
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from sqlalchemy.orm import Session
import uuid
from app.models.models import Milestone, Observation, ObservationType

class ObservationIntelligenceEngine:
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self._model = None
        self.model_version = "oie_v1_multilingual"
        self.milestone_ids: List[Any] = []
        self.milestone_vectors: np.ndarray = np.empty((0, 384))
        self.milestone_metadata: Dict[Any, Dict[str, Any]] = {}
        self.default_threshold: float = 0.45

        # Local transliteration map for Hinglish expressions
        self.transliteration_glossary = {
            # Existing mappings
            "ishaara": "pointing", "ishara": "pointing",
            "khaana": "food", "khana": "food",
            "bolna": "speaking", "bola": "said",
            "chala": "walked", "chalna": "walking",

            # Body Parts
            "aankh": "eye",
            "aankhen": "eyes",
            "kaan": "ear",
            "kaanon": "ears",
            "naak": "nose",
            "haath": "hand",
            "pair": "foot",
            "ungli": "finger",
            "ungliyon": "fingers",
            "angutha": "thumb",
            "anguthe": "thumb",

            # Communication
            "bolo": "speak",
            "bol": "speak",
            "bolta": "speaks",
            "bolti": "speaks",
            "baat": "talk",
            "baatein": "conversation",
            "pooch": "ask",
            "poochta": "asks",
            "poochti": "asks",
            "jawab": "answer",
            "suno": "listen",
            "dikhao": "show",
            "dekho": "look",

            # Emotions
            "gussa": "anger",
            "gusse": "angry",
            "khush": "happy",
            "dukhi": "sad",
            "rota": "crying",
            "rote": "crying",
            "rona": "cry",
            "roti": "crying",
            "darr": "fear",

            # Social
            "dost": "friend",
            "baccha": "child",
            "bacche": "children",
            "bacho": "children",
            "mummy": "mother",
            "papa": "father",
            "dada": "grandfather",
            "dadi": "grandmother",
            "gale": "hug",

            # Play
            "khel": "play",
            "khelna": "play",
            "khelta": "playing",
            "khelti": "playing",
            "khilona": "toy",
            "khilone": "toys",
            "gudiya": "doll",

            # Movement
            "chal": "walk",
            "chalta": "walking",
            "chalti": "walking",
            "daud": "run",
            "daudta": "running",
            "daudti": "running",
            "kood": "hop",
            "koodna": "hopping",
            "chadha": "climbed",
            "chadhna": "climb",
            "seedhi": "stairs",
            "seedhiyan": "stairs",
            "seedhiyon": "stairs",

            # Objects
            "chammach": "spoon",
            "plate": "plate",
            "dabba": "box",
            "dabbe": "box",
            "gadi": "car",
            "gaadi": "car",

            # Phase 5A.3 Additional Mappings
            "dekhta": "looks",
            "dekhte": "looking",
            "dekha": "looked",
            "dekhkar": "looking",
            "aaya": "came",
            "daal": "put",
            "daala": "put",
            "daali": "put",
            "rakha": "kept",
            "rakhi": "kept",
            "bataya": "told",
            "bina": "without",
            "atkan": "stutter",
            "atke": "stutter",
            "anjaan": "stranger",
            "pata": "knows",
            "kahani": "story",
            "sach": "real",
            "jaise": "similar",
            "sath": "together",
            "alag": "different",
            "bana": "make",
            "nahi": "not",
            "hota": "is"
        }

    @property
    def model(self):
        if self._model is None:
            print("[INFO] Lazy loading SentenceTransformer model...")
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def preprocess_text(self, text: str) -> str:
        """Translates localized Hinglish terms to English equivalents, preserving casing and punctuation."""
        def replace_word(match):
            word = match.group(0)
            lower_word = word.lower()
            if lower_word in self.transliteration_glossary:
                translated = self.transliteration_glossary[lower_word]
                if word.isupper():
                    return translated.upper()
                elif word[0].isupper():
                    return translated.capitalize()
                return translated
            return word
        return re.sub(r"\b\w+\b", replace_word, text)

    def initialize_cache(self, db: Session):
        """Pre-computes and caches milestone embeddings on startup."""
        milestones = db.query(Milestone).all()
        if not milestones:
            raise RuntimeError(
                "Milestone cache empty: Database contains 0 milestones. "
                "Please seed the database before starting the application."
            )

        texts = []
        self.milestone_ids = []
        self.milestone_metadata = {}

        for m in milestones:
            # Construct milestone text
            text = f"{m.title} {m.description} {m.domain.name}"
            texts.append(text)
            self.milestone_ids.append(m.id)
            self.milestone_metadata[m.id] = {
                "id": m.id,
                "title": m.title,
                "description": m.description,
                "domain_name": m.domain.name,
                "domain_id": m.domain_id,
                "age_range_low": m.age_range_low,
                "age_range_high": m.age_range_high
            }

        # Generate embeddings
        vectors = self.model.encode(texts, convert_to_numpy=True)
        # L2 normalization for fast cosine similarity dot product calculation
        self.milestone_vectors = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)

    def calculate_age_weight(self, child_age_months: int, age_low: int, age_high: int) -> float:
        """Calculates age band weighting for milestone retrieval decay."""
        if age_low <= child_age_months <= age_high:
            return 1.0
        elif child_age_months > age_high:
            # Older child (checking for developmental delays)
            return max(0.4, 1.0 - 0.05 * (child_age_months - age_high))
        else:
            # Younger child (preventing advanced matches)
            return max(0.1, 1.0 - 0.15 * (age_low - child_age_months))

    def get_relevance_label(self, score: float) -> str:
        """Converts similarity score into a non-clinical relevance label."""
        if score >= 0.65:
            return "Strong relevance"
        elif score >= 0.52:
            return "Moderate relevance"
        return "Possible relevance"

    def retrieve_domains(self, obs_vector: np.ndarray, child_age_months: int) -> List[Dict[str, Any]]:
        """Ranks developmental domains based on cached milestone similarities."""
        if len(self.milestone_ids) == 0:
            return []
            
        similarities = np.dot(self.milestone_vectors, obs_vector)
        domain_sims = {}

        for idx, m_id in enumerate(self.milestone_ids):
            m = self.milestone_metadata[m_id]
            weight = self.calculate_age_weight(child_age_months, m["age_range_low"], m["age_range_high"])
            final_score = float(similarities[idx] * weight)
            domain_sims.setdefault(m["domain_name"], []).append(final_score)

        domain_results = []
        for d_name, scores in domain_sims.items():
            max_score = max(scores) if scores else 0.0
            if max_score >= 0.35:
                domain_results.append({
                    "domain_name": d_name,
                    "relevance_score": round(max_score, 3),
                    "relevance_label": self.get_relevance_label(max_score)
                })

        return sorted(domain_results, key=lambda x: x["relevance_score"], reverse=True)[:3]

    def retrieve_milestones(self, obs_vector: np.ndarray, child_age_months: int, threshold: float = 0.45) -> List[Dict[str, Any]]:
        """Retrieves and ranks the top matching milestones above the threshold."""
        if len(self.milestone_ids) == 0:
            return []
            
        similarities = np.dot(self.milestone_vectors, obs_vector)
        suggestions = []

        for idx, m_id in enumerate(self.milestone_ids):
            m = self.milestone_metadata[m_id]
            weight = self.calculate_age_weight(child_age_months, m["age_range_low"], m["age_range_high"])
            final_score = float(similarities[idx] * weight)

            if final_score >= threshold:
                suggestions.append({
                    "milestone_id": m["id"],
                    "title": m["title"],
                    "relevance_score": round(final_score, 3),
                    "relevance_label": self.get_relevance_label(final_score)
                })

        return sorted(suggestions, key=lambda x: x["relevance_score"], reverse=True)[:3]

# Singleton engine instance
ai_engine = ObservationIntelligenceEngine()


def detect_recurrence(db: Session, child_id: uuid.UUID, new_observation: Observation) -> Optional[uuid.UUID]:
    """Detects if a new concern is a recurrence of a previous concern (similarity >= 0.70)."""
    print(f"[DEBUG] detect_recurrence called. Type: {new_observation.entry_type}")
    if new_observation.entry_type != ObservationType.CONCERN:
        print("[DEBUG] Not concern type")
        return None

    # Ensure new observation has an embedding
    if not new_observation.embedding_vector:
        preprocessed = ai_engine.preprocess_text(new_observation.body)
        new_vector = ai_engine.model.encode(preprocessed, convert_to_numpy=True)
        new_observation.embedding_vector = new_vector.tolist()
    else:
        new_vector = np.array(new_observation.embedding_vector)

    # Normalize new vector
    new_vector_norm = new_vector / np.linalg.norm(new_vector)

    # Fetch prior concerns for this child that are at least 14 days older
    from datetime import timedelta
    cutoff_date = new_observation.observed_at - timedelta(days=14)
    print(f"[DEBUG] cutoff_date: {cutoff_date}, new_obs.observed_at: {new_observation.observed_at}")
    
    prior_concerns = db.query(Observation).filter(
        Observation.child_id == child_id,
        Observation.entry_type == ObservationType.CONCERN,
        Observation.id != new_observation.id,
        Observation.observed_at <= cutoff_date,
        Observation.deleted_at.is_(None)
    ).all()

    print(f"[DEBUG] Found {len(prior_concerns)} prior concerns.")
    if not prior_concerns:
        return None

    best_similarity = -1.0
    best_match = None

    for prior in prior_concerns:
        if not prior.embedding_vector:
            preprocessed_prior = ai_engine.preprocess_text(prior.body)
            p_vector = ai_engine.model.encode(preprocessed_prior, convert_to_numpy=True)
            prior.embedding_vector = p_vector.tolist()
            db.add(prior)
        else:
            p_vector = np.array(prior.embedding_vector)

        p_vector_norm = p_vector / np.linalg.norm(p_vector)
        similarity = float(np.dot(new_vector_norm, p_vector_norm))
        print(f"[DEBUG] Comparing '{new_observation.body}' with '{prior.body}': similarity = {similarity}")

        if similarity > best_similarity:
            best_similarity = similarity
            best_match = prior

    print(f"[DEBUG] best_similarity: {best_similarity}")
    if best_similarity >= 0.70 and best_match is not None:
        if best_match.recurrence_group_id:
            new_observation.recurrence_group_id = best_match.recurrence_group_id
        else:
            new_group_id = uuid.uuid4()
            best_match.recurrence_group_id = new_group_id
            new_observation.recurrence_group_id = new_group_id
            db.add(best_match)
        return new_observation.recurrence_group_id

    return None
