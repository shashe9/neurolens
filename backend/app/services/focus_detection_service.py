import re
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import Observation, ObservationType, MilestoneStatus, Milestone, DevelopmentalDomain

THEMES = {
    "communication": {
        "keywords": [r"communicat", r"speak", r"spoke", r"word", r"words", r"talk", r"talked", r"say", r"said", r"call", r"called", r"express", r"expressing", r"expressive", r"expresses", r"vocalize", r"vocal", r"sounds"],
        "summary_many": "Many recent observations involve communication attempts.",
        "summary_few": "Several observations relate to communication attempts."
    },
    "social_interaction": {
        "keywords": [r"social", r"friend", r"play with", r"smile", r"gaze", r"eye contact", r"peer", r"interact", r"interactive", r"parent", r"mother", r"father", r"caregiver", r"share", r"sharing", r"look at me", r"look back"],
        "summary_many": "Recent logs frequently mention social interactions during play.",
        "summary_few": "Several logs mention social interactions."
    },
    "gestures": {
        "keywords": [r"gesture", r"point", r"pointed", r"wave", r"waved", r"nod", r"nodded", r"shake head", r"shook head", r"pointing", r"hand movement", r"beckon", r"motions"],
        "summary_many": "Multiple observations note the use of gestures or pointing.",
        "summary_few": "A few observations note gestures or pointing."
    },
    "play_behavior": {
        "keywords": [r"play", r"toy", r"toys", r"block", r"blocks", r"doll", r"dolls", r"lego", r"pretend", r"game", r"imaginative", r"stack", r"stacking", r"roll", r"rolling", r"blocks", r"cars", r"puzzles"],
        "summary_many": "Recent logs describe active play behaviors or toy interactions.",
        "summary_few": "Several logs describe play behaviors."
    },
    "emotional_regulation": {
        "keywords": [r"cry", r"cried", r"crying", r"upset", r"frustrated", r"frustration", r"temper", r"tantrum", r"calm", r"soothe", r"regulate", r"emotional", r"emotion", r"anger", r"angry", r"sad", r"happy", r"laugh", r"screaming", r"shout"],
        "summary_many": "Many recent logs capture emotional regulation and expressions.",
        "summary_few": "A few logs capture emotional regulation."
    },
    "motor_activity": {
        "keywords": [r"motor", r"run", r"running", r"jump", r"jumping", r"climb", r"climbing", r"walk", r"walking", r"scribble", r"scribbling", r"draw", r"drawing", r"finger", r"hand", r"foot", r"hop", r"hopping", r"crawl", r"crawling", r"steps", r"movement", r"threw", r"catch"],
        "summary_many": "Multiple logs capture gross or fine motor activities.",
        "summary_few": "Several logs capture motor activities."
    },
    "daily_routines": {
        "keywords": [r"eat", r"eating", r"meal", r"meals", r"dinner", r"lunch", r"breakfast", r"sleep", r"sleeping", r"bedtime", r"bath", r"dress", r"dressing", r"brush", r"brushing", r"food", r"utensil", r"spoon", r"cup", r"bottle", r"diaper", r"potty"],
        "summary_many": "Recent entries highlight interactions during daily routines.",
        "summary_few": "A few entries highlight daily routines."
    }
}

DOMAIN_PROMPTS = {
    "Communication": [
        "Have you noticed how your child responds when they hear their name called?",
        "Have you observed your child making sounds or using simple words to get attention?"
    ],
    "Gross Motor": [
        "Have you noticed your child climbing on furniture or steps?",
        "Have you observed how your child kicks or throws a ball?"
    ],
    "Fine Motor": [
        "Have you observed how your child turns pages in a book?",
        "Have you noticed how your child stacks small blocks or holds a crayon?"
    ],
    "Social Emotional": [
        "Have you observed your child pointing to show you something interesting?",
        "Have you noticed how your child behaves when playing near other children?"
    ],
    "Cognitive": [
        "Have you noticed if your child points to body parts or pictures when asked?",
        "Have you observed your child trying to scribble or play with simple puzzles?"
    ],
    "Behavioral Patterns": [
        "Have you noticed any repetitive routines during play?",
        "Have you observed your child's reaction to changes in their routine?"
    ]
}

def analyze_developmental_focus(observations: List[Observation]) -> List[Dict[str, Any]]:
    """
    Feature 2: Analyzes observations and detects recurring focus themes deterministically.
    """
    counts = {theme: 0 for theme in THEMES}
    
    for obs in observations:
        text = (obs.structured_body or obs.body or "").lower()
        for theme, config in THEMES.items():
            if any(re.search(pat, text) for pat in config["keywords"]):
                counts[theme] += 1
                
    results = []
    for theme, count in counts.items():
        if count >= 2:
            config = THEMES[theme]
            summary = config["summary_many"] if count >= 3 else config["summary_few"]
            results.append({
                "theme": theme,
                "count": count,
                "summary": summary
            })
            
    # Sort by count descending
    return sorted(results, key=lambda x: x["count"], reverse=True)

def detect_blind_spots(db: Session, child_id: uuid.UUID, observations: List[Observation]) -> List[Dict[str, Any]]:
    """
    Feature 3: Identifies domains with low coverage in the last 30 days and suggests observation prompts.
    """
    now = datetime.utcnow()
    t30 = now - timedelta(days=30)
    
    recent_obs = [o for o in observations if o.observed_at >= t30]
    domains = db.query(DevelopmentalDomain).all()
    
    domain_counts = {d.name: 0 for d in domains}
    for o in recent_obs:
        if o.domain:
            domain_counts[o.domain.name] = domain_counts.get(o.domain.name, 0) + 1
            
    blind_spots = []
    for d in domains:
        count = domain_counts.get(d.name, 0)
        if count < 2:  # Threshold for low information
            prompts = DOMAIN_PROMPTS.get(d.name, [
                f"Have you noticed any recent developments in the {d.name.lower()} area?",
                f"Observe how your child plays in tasks involving {d.name.lower()}."
            ])
            blind_spots.append({
                "domain_name": d.name,
                "count": count,
                "summary": f"We have very little recent information about {d.name.lower()}.",
                "prompts": prompts
            })
            
    return blind_spots

def generate_visit_prep(db: Session, child_id: uuid.UUID, observations: List[Observation]) -> Dict[str, Any]:
    """
    Feature 4: Generates Visit Preparation elements (Things Worth Discussing, Recent Positive Changes, Suggested Topics).
    """
    # 1. Things Worth Discussing
    discussing = []
    
    # Check for recurring concerns
    from app.services.report_service import get_persistent_concerns
    persistent = get_persistent_concerns(db, child_id)
    if persistent:
        discussing.append("Communication concerns have appeared across multiple weeks.")
        for p in persistent:
            first_body = p["first_occurrence"]["body"].lower()
            if "frustrated" in first_body or "cry" in first_body or "difficult" in first_body:
                discussing.append("Several observations mention frustration during communication.")
                break
                
    # Check for regressions
    regressions = [o for o in observations if o.is_regression]
    if regressions:
        discussing.append(f"Skill regressions have been reported in the past period: '{regressions[0].body}'")
        
    # Check for peer interaction concerns
    for o in observations:
        if o.entry_type == ObservationType.CONCERN:
            body_l = o.body.lower()
            if "peer" in body_l or "other children" in body_l or "friend" in body_l:
                discussing.append("Parent has logged concerns related to peer interaction.")
                break
                
    if not discussing:
        discussing.append("General developmental monitoring — no persistent concern patterns flagged.")

    # 2. Recent Positive Changes
    positive_changes = []
    
    # Milestone achievements
    recent_achievements = db.query(MilestoneStatus).filter(
        MilestoneStatus.child_id == child_id,
        MilestoneStatus.status.in_(["observed", "consistently_demonstrated"])
    ).order_by(MilestoneStatus.updated_at.desc()).limit(3).all()
    
    for ms in recent_achievements:
        positive_changes.append(f"Achieved milestone: '{ms.milestone.title}' in {ms.milestone.domain.name}.")
        
    # Check text bodies for indicators
    for o in observations:
        body_l = o.body.lower()
        if "independent" in body_l or "learned" in body_l or "new word" in body_l:
            positive_changes.append(f"Caregiver noted progress: '{o.body}'")
            break
            
    if not positive_changes:
        positive_changes.append("Child is actively practicing skills across multiple developmental domains.")

    # 3. Suggested Topics
    topics = []
    if persistent:
        topics.append("Expressive language & communication frustration")
    if any("peer" in o.body.lower() for o in observations):
        topics.append("Social interaction patterns with peers")
    if not topics:
        topics.append("Expressive language and developmental progression")
    topics.append("Gross or fine motor skill progression")
    
    return {
        "things_worth_discussing": discussing,
        "recent_positive_changes": positive_changes,
        "suggested_topics": topics
    }

def generate_parent_narrative(db: Session, child_id: uuid.UUID, observations: List[Observation]) -> str:
    """
    Feature 5: Generates a developmental storytelling paragraph grounded completely in observations.
    """
    from app.models.models import Child, ObservationType
    child = db.query(Child).filter(Child.id == child_id).first()
    first_name = child.display_first_name if child else "your child"
    
    if not observations:
        return f"No observations have been logged for {first_name} in this period. Start logging to build their developmental story."
        
    # Segment observations
    positive_moments = [o for o in observations if o.entry_type in [ObservationType.MILESTONE, ObservationType.GENERAL]]
    concerns = [o for o in observations if o.entry_type == ObservationType.CONCERN]
    regressions = [o for o in observations if o.is_regression]

    # Group by domain
    domain_counts = {}
    for o in observations:
        if o.domain:
            d_name = o.domain.name.lower().replace("_", " ")
            domain_counts[d_name] = domain_counts.get(d_name, 0) + 1

    parts = []
    
    # 1. Introduction with exact counts and domain names
    domain_summary_parts = [f"{count} in {dom}" for dom, count in domain_counts.items()]
    if domain_summary_parts:
        summary_str = ", including " + ", ".join(domain_summary_parts)
    else:
        summary_str = ""

    parts.append(f"Over the last month, we analyzed {len(observations)} observation logs for {first_name}{summary_str}.")

    # 2. Add Child-Specific Quotes/Paraphrases
    if positive_moments:
        latest_pos = positive_moments[0]
        # Clean quote a bit
        snippet = latest_pos.body.strip()
        if not snippet.endswith(('.', '!', '?')):
            snippet += "."
        parts.append(f"In a positive milestone, you observed {first_name} showing growth. For instance, on {latest_pos.observed_at.strftime('%B %d')}, you logged: \"{snippet}\"")
        
        # Add details of what this suggests
        pos_actions = []
        for o in positive_moments:
            body_lower = o.body.lower()
            if "point" in body_lower:
                pos_actions.append("using communicative gestures to share focus")
            if "speak" in body_lower or "word" in body_lower or "say" in body_lower or "said" in body_lower:
                pos_actions.append("building spoken vocabulary")
            if "look" in body_lower or "eye" in body_lower or "face" in body_lower:
                pos_actions.append("connecting through eye gaze")
            if "play" in body_lower or "toy" in body_lower or "block" in body_lower:
                pos_actions.append("learning through interactive play")
        
        pos_actions = list(dict.fromkeys(pos_actions))
        if pos_actions:
            parts.append(f"This reflects active development in {', '.join(pos_actions[:2])}.")
            
    # 3. Add Concern Details
    if concerns:
        latest_con = concerns[0]
        snippet_con = latest_con.body.strip()
        if not snippet_con.endswith(('.', '!', '?')):
            snippet_con += "."
        parts.append(f"Caregiver tracking also identified developmental questions. Specifically, you noted: \"{snippet_con}\"")
        
        con_actions = []
        for o in concerns:
            body_lower = o.body.lower()
            if "respond" in body_lower or "name" in body_lower or "call" in body_lower:
                con_actions.append("responding consistently to auditory name cues")
            if "look" in body_lower or "eye" in body_lower or "face" in body_lower:
                con_actions.append("maintaining joint visual engagement")
            else:
                con_actions.append("developing focused play behaviors")
        con_actions = list(dict.fromkeys(con_actions))
        if con_actions:
            parts.append(f"We are monitoring progress to support {first_name} in {', '.join(con_actions[:2])}.")
    elif regressions:
        parts.append(f"Your records note a skill regression: \"{regressions[0].body}\". We will track this closely to discuss with your provider.")
    else:
        parts.append(f"Currently, {first_name} is showing steady developmental practice without any signs of regression or persistent flags.")

    parts.append("These observations provide invaluable data for your clinician to build a complete developmental trajectory.")

    return " ".join(parts)

