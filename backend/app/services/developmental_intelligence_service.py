import re
import uuid
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from app.models.models import (
    Child, Observation, ObservationType, DevelopmentalDomain,
    MilestoneStatus, Milestone, First, ClinicalVisit
)
from app.services.report_service import calculate_observation_quality

# Mapping keywords to parent-friendly theme names
THEMES_MAPPING = {
    "Communication": [r"communicat", r"speak", r"spoke", r"word", r"words", r"talk", r"talked", r"say", r"said", r"call", r"called", r"express", r"expressing", r"expressive", r"expresses", r"vocalize", r"vocal", r"sounds"],
    "Social Interaction": [r"social", r"friend", r"play with", r"smile", r"gaze", r"eye contact", r"peer", r"interact", r"interactive", r"parent", r"mother", r"father", r"caregiver", r"share", r"sharing", r"look at me", r"look back"],
    "Joint Attention": [r"gesture", r"point", r"pointed", r"wave", r"waved", r"nod", r"nodded", r"shake head", r"shook head", r"pointing", r"hand movement", r"beckon", r"motions", r"joint attention", r"show", r"showing"],
    "Emotional Expression": [r"cry", r"cried", r"crying", r"upset", r"frustrated", r"frustration", r"temper", r"tantrum", r"calm", r"soothe", r"regulate", r"emotional", r"emotion", r"anger", r"angry", r"sad", r"happy", r"laugh", r"screaming", r"shout"],
    "Pretend Play": [r"play", r"toy", r"toys", r"block", r"blocks", r"doll", r"dolls", r"lego", r"pretend", r"game", r"imaginative", r"stack", r"stacking", r"roll", r"rolling", r"cars", r"puzzles"],
    "Gross Motor": [r"motor", r"run", r"running", r"jump", r"jumping", r"climb", r"climbing", r"walk", r"walking", r"hop", r"hopping", r"crawl", r"crawling", r"steps", r"movement", r"threw", r"catch"],
    "Fine Motor": [r"scribble", r"scribbling", r"draw", r"drawing", r"finger", r"hand", r"crayon", r"pencil", r"button", r"buttoning", r"zipper", r"zip", r"hold"],
    "Daily Living": [r"eat", r"eating", r"meal", r"meals", r"dinner", r"lunch", r"breakfast", r"sleep", r"sleeping", r"bedtime", r"bath", r"dress", r"dressing", r"brush", r"brushing", r"food", r"utensil", r"spoon", r"cup", r"bottle", r"diaper", r"potty"]
}

DOMAIN_PROMPTS = {
    "Communication": [
        "Have you noticed how your child responds when they hear their name called?",
        "Have you observed your child making sounds or using simple words to get attention?"
    ],
    "Social Emotional": [
        "Have you observed your child pointing to show you something interesting?",
        "Have you noticed how your child behaves when playing near other children?"
    ],
    "Gross Motor": [
        "Have you noticed your child climbing on furniture or steps?",
        "Have you observed how your child kicks or throws a ball?"
    ],
    "Fine Motor": [
        "Have you observed how your child turns pages in a book?",
        "Have you noticed how your child stacks small blocks or holds a crayon?"
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

AGE_SPECIFIC_QUESTIONS = {
    (0, 12): [
        "Have you noticed your child turning their head towards your voice?",
        "Have you observed your child smiling in response to your smiles or laughs?",
        "Have you noticed your baby reaching for their favorite toys during floor play?",
        "Have you noticed them making babbling sounds like 'ba-ba' or 'da-da'?"
    ],
    (13, 18): [
        "Have you noticed your child waving 'hello' or 'goodbye' when someone arrives or leaves?",
        "Have you observed your child pointing to a toy they want you to see?",
        "Have you noticed them using single words to request their favorite foods or items?",
        "Have you noticed your child trying to scribble on paper if given a crayon?"
    ],
    (19, 24): [
        "Have you noticed your child bringing objects to show you just to share their excitement?",
        "Have you observed pretend play, like feeding a stuffed animal or doll?",
        "Have you noticed your child putting two words together, like 'more milk' or 'big ball'?",
        "Have you observed them trying to use utensils or drinking from an open cup during meals?"
    ],
    (25, 36): [
        "Have you noticed pretend play with simple toys, like pretending a block is a phone?",
        "Have you observed your child climbing up and down steps or small play structures?",
        "Have you noticed them asking simple questions like 'what's that?' or 'where is toy?'",
        "Have you noticed your child describing something that happened earlier today?"
    ],
    (37, 120): [
        "Have you observed your child playing simple games with other kids, like tag or hide and seek?",
        "Have you noticed them using 4 or 5-word sentences when describing their day?",
        "Have you observed them expressing a wide range of emotions and talking about how they feel?",
        "Have you noticed your child doing simple puzzles or sorting objects by shape or color?"
    ]
}

FIRST_CANDIDATE_PATTERNS = [
    (r"\bfirst word\b|first words", "First Word"),
    (r"\bfirst two-word\b|\bfirst sentence\b", "First Two-Word Phrase"),
    (r"\bfirst pointing\b|\bpoint\b.*\bfirst time\b", "First Pointing Moment"),
    (r"\bfirst pretend play\b|\bpretend play\b.*\bfirst time\b", "First Pretend Play"),
    (r"\bfirst spoon use\b|\bspoon\b.*\bfirst time\b|\bindependent spoon\b", "First Independent Spoon Use"),
    (r"\bfirst step\b|\bfirst steps\b", "First Independent Steps"),
    (r"\bfirst wave\b|\bwave\b.*\bfirst time\b", "First Waving Hello/Goodbye")
]


def extract_developmental_themes(observations: List[Observation]) -> List[str]:
    """Identifies recurring themes from observations."""
    counts = {theme: 0 for theme in THEMES_MAPPING}
    for obs in observations:
        text = (obs.structured_body or obs.body or "").lower()
        for theme, keywords in THEMES_MAPPING.items():
            if any(re.search(pat, text) for pat in keywords):
                counts[theme] += 1
    # Sort themes by count, filtering to themes with count > 0
    return sorted([t for t, c in counts.items() if c > 0], key=lambda t: counts[t], reverse=True)


def detect_first_candidate(text: str) -> Optional[str]:
    """Scans text for phrases that might indicate a meaningful developmental first."""
    text_lower = text.lower()
    for pattern, title in FIRST_CANDIDATE_PATTERNS:
        if re.search(pattern, text_lower):
            return title
    return None


def generate_monthly_snapshot(db: Session, child_id: uuid.UUID, month_str: Optional[str] = None) -> Dict[str, Any]:
    """Generates a structured monthly snapshot of child developmental activities and observations."""
    if month_str:
        year, month = map(int, month_str.split("-"))
    else:
        now = datetime.utcnow()
        year, month = now.year, now.month
        month_str = f"{year:04d}-{month:02d}"

    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    # Observations in this month
    obs_this_month = db.query(Observation).filter(
        Observation.child_id == child_id,
        Observation.observed_at >= start_date,
        Observation.observed_at < end_date,
        Observation.deleted_at.is_(None)
    ).all()

    # Domains count
    domains_count = {}
    domains = db.query(DevelopmentalDomain).all()
    for d in domains:
        normalized_name = d.name.lower().replace(" ", "_")
        domains_count[normalized_name] = 0

    for o in obs_this_month:
        if o.domain:
            normalized_name = o.domain.name.lower().replace(" ", "_")
            domains_count[normalized_name] = domains_count.get(normalized_name, 0) + 1

    # Milestones achieved this month
    achieved_statuses = db.query(MilestoneStatus).filter(
        MilestoneStatus.child_id == child_id,
        MilestoneStatus.status.in_(["achieved", "observed", "consistently_demonstrated"])
    ).all()

    milestones_this_month = []
    for ms in achieved_statuses:
        status_date = ms.observed_date if ms.observed_date else ms.updated_at.date()
        if start_date.date() <= status_date < end_date.date():
            milestones_this_month.append({
                "id": str(ms.milestone_id),
                "title": ms.milestone.title,
                "domain": ms.milestone.domain.name
            })

    # Firsts in this month
    firsts_this_month = db.query(First).filter(
        First.child_id == child_id,
        First.first_date >= start_date.date(),
        First.first_date < end_date.date()
    ).all()

    firsts_data = [{
        "id": str(f.id),
        "is_first": f.is_first,
        "first_title": f.first_title,
        "first_date": f.first_date.isoformat(),
        "linked_observation_id": str(f.linked_observation_id) if f.linked_observation_id else None
    } for f in firsts_this_month]

    # Concerns in this month
    concerns_this_month = [o for o in obs_this_month if o.entry_type == ObservationType.CONCERN]
    
    # Concerns in previous months (before start_date)
    concerns_prev_months = db.query(Observation).filter(
        Observation.child_id == child_id,
        Observation.entry_type == ObservationType.CONCERN,
        Observation.observed_at < start_date,
        Observation.deleted_at.is_(None)
    ).all()

    prev_group_ids = {str(c.recurrence_group_id) for c in concerns_prev_months if c.recurrence_group_id}
    this_group_ids = {str(c.recurrence_group_id) for c in concerns_this_month if c.recurrence_group_id}

    persistent_groups = prev_group_ids.intersection(this_group_ids)
    new_groups = this_group_ids - prev_group_ids
    resolved_groups = prev_group_ids - this_group_ids

    persistent_concerns = []
    new_concerns = []
    resolved_concerns = []

    for c in concerns_this_month:
        g_id = str(c.recurrence_group_id) if c.recurrence_group_id else None
        if g_id in persistent_groups:
            if g_id not in [p["recurrence_group_id"] for p in persistent_concerns]:
                persistent_concerns.append({
                    "recurrence_group_id": g_id,
                    "body": c.body,
                    "observed_at": c.observed_at.isoformat()
                })
        elif g_id in new_groups or g_id is None:
            new_concerns.append({
                "recurrence_group_id": g_id,
                "body": c.body,
                "observed_at": c.observed_at.isoformat()
            })

    resolved_map = {}
    for c in concerns_prev_months:
        g_id = str(c.recurrence_group_id) if c.recurrence_group_id else None
        if g_id in resolved_groups:
            if g_id not in resolved_map or c.observed_at > resolved_map[g_id].observed_at:
                resolved_map[g_id] = c

    for g_id, c in resolved_map.items():
        resolved_concerns.append({
            "recurrence_group_id": g_id,
            "body": c.body,
            "observed_at": c.observed_at.isoformat()
        })

    active_themes = extract_developmental_themes(obs_this_month)
    quality_data = calculate_observation_quality(obs_this_month)

    # Developmental Signals structure to save/cache
    signals = {
        "month": month_str,
        "observation_count": len(obs_this_month),
        "domains": domains_count,
        "milestones_achieved": milestones_this_month,
        "firsts": firsts_data,
        "persistent_concerns": persistent_concerns,
        "resolved_concerns": resolved_concerns,
        "new_concerns": new_concerns,
        "active_themes": active_themes,
        "observation_quality": quality_data["quality_level"]
    }

    return signals


def calculate_domain_trends(current_counts: Dict[str, int], previous_counts: Dict[str, int]) -> Dict[str, str]:
    """Computes UP, DOWN, or STEADY trends comparing current month vs previous month counts."""
    trends = {}
    for key in current_counts:
        curr = current_counts.get(key, 0)
        prev = previous_counts.get(key, 0)
        if curr > prev:
            trends[key] = "UP"
        elif curr < prev:
            trends[key] = "DOWN"
        else:
            trends[key] = "STEADY"
    return trends


def generate_child_snapshot(db: Session, child_id: uuid.UUID) -> Dict[str, Any]:
    """Generates the high-level Child Snapshot for the dashboard hero section."""
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise ValueError("Child profile not found.")

    age_months = (datetime.utcnow().date() - child.date_of_birth).days // 30
    month_str = datetime.utcnow().strftime("%Y-%m")
    snapshot = generate_monthly_snapshot(db, child_id, month_str)

    # Determine most observed area
    most_observed_area = "None"
    max_count = 0
    for d_name, d_count in snapshot["domains"].items():
        if d_count > max_count:
            max_count = d_count
            most_observed_area = d_name.replace("_", " ").capitalize()

    # Growth highlight
    growth_highlight = "No recent growth highlights logged"
    if snapshot["firsts"]:
        growth_highlight = f"First milestone: '{snapshot['firsts'][0]['first_title']}' was recorded"
    elif snapshot["milestones_achieved"]:
        growth_highlight = f"Achieved milestone: '{snapshot['milestones_achieved'][0]['title']}'"
    else:
        # Fallback: get the latest general observation
        latest_obs = db.query(Observation).filter(
            Observation.child_id == child_id,
            Observation.entry_type == ObservationType.GENERAL,
            Observation.deleted_at.is_(None)
        ).order_by(Observation.observed_at.desc()).first()
        if latest_obs:
            growth_highlight = f"Observed activity: '{latest_obs.body[:40]}...'"

    # Watch item
    watch_item = "No active concern patterns flagged"
    if snapshot["persistent_concerns"]:
        watch_item = f"Continued monitoring of: '{snapshot['persistent_concerns'][0]['body'][:50]}...'"
    elif snapshot["new_concerns"]:
        watch_item = f"New focus observed: '{snapshot['new_concerns'][0]['body'][:50]}...'"

    # Next appointment
    next_apt = db.query(ClinicalVisit).filter(
        ClinicalVisit.child_id == child_id,
        ClinicalVisit.visit_date >= date.today()
    ).order_by(ClinicalVisit.visit_date.asc()).first()

    next_appointment = next_apt.visit_date.isoformat() if next_apt else "No appointment scheduled"

    return {
        "child_name": f"{child.display_first_name} {child.display_last_name}",
        "age_months": age_months,
        "tracking_start_date": child.created_at.date().isoformat(),
        "most_observed_area": most_observed_area,
        "growth_highlight": growth_highlight,
        "watch_item": watch_item,
        "next_appointment": next_appointment
    }


def generate_growth_story(db: Session, child_id: uuid.UUID, month_str: Optional[str] = None) -> Dict[str, Any]:
    """Generates the monthly narrative growth story for the child."""
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise ValueError("Child profile not found.")

    first_name = child.display_first_name

    if month_str:
        year, month = map(int, month_str.split("-"))
    else:
        now = datetime.utcnow()
        year, month = now.year, now.month
        month_str = f"{year:04d}-{month:02d}"

    month_name = datetime(year, month, 1).strftime("%B")
    snapshot = generate_monthly_snapshot(db, child_id, month_str)

    obs_count = snapshot["observation_count"]
    themes = snapshot["active_themes"]
    milestones = snapshot["milestones_achieved"]
    firsts = snapshot["firsts"]
    persistent = snapshot["persistent_concerns"]
    new_concerns = snapshot["new_concerns"]

    story_parts = []

    if obs_count == 0:
        story_parts.append(f"In {month_name}, you didn't have a chance to log any daily moments for {first_name} yet.")
        story_parts.append(f"Logging even a few moments each week can help capture {first_name}'s unique developmental journey and highlight the small milestones along the way.")
    else:
        if obs_count == 1:
            story_parts.append(f"In {month_name}, you captured one special moment from {first_name}'s daily life.")
        else:
            story_parts.append(f"In {month_name}, you captured {obs_count} moments from {first_name}'s daily life.")

        if themes:
            if len(themes) == 1:
                story_parts.append(f"Many of your observations this month focused on {themes[0].lower()}.")
            elif len(themes) >= 2:
                story_parts.append(f"Many of your observations involved {themes[0].lower()} and {themes[1].lower()}.")
        else:
            story_parts.append("These entries span various areas of daily play and interaction.")

        growth_sentences = []
        if firsts:
            first_titles = [f["first_title"] for f in firsts]
            if len(first_titles) == 1:
                growth_sentences.append(f"A wonderful highlight was marking a significant first milestone: '{first_titles[0]}'.")
            else:
                growth_sentences.append(f"A wonderful highlight was marking significant first milestones: {', '.join(first_titles[:-1])} and {first_titles[-1]}.")

        if milestones:
            milestone_titles = [m["title"] for m in milestones]
            if len(milestone_titles) == 1:
                growth_sentences.append(f"{first_name} successfully achieved a milestone you had been watching: '{milestone_titles[0]}'.")
            else:
                growth_sentences.append(f"{first_name} successfully completed several milestones, including {', '.join(f'\'{t}\'' for t in milestone_titles[:2])}.")

        if growth_sentences:
            story_parts.append(" ".join(growth_sentences))
        else:
            story_parts.append(f"It has been wonderful to observe {first_name} actively exploring new skills and engaging with their surroundings.")

        concern_sentences = []
        all_concerns = persistent + [c for c in new_concerns if c.get("recurrence_group_id") is not None]
        if all_concerns:
            concern_sentences.append("You also continued monitoring and keeping a close eye on moments of challenge, particularly when communication or transitions became difficult.")
        else:
            concern_sentences.append("You kept a steady eye on daily interactions, focusing on positive steps and natural progressions.")

        story_parts.append(" ".join(concern_sentences))
        story_parts.append(f"These observations build a grounded, beautiful story of {first_name}'s unique growth over the course of {month_name}.")

    story_body = " ".join(story_parts)

    return {
        "title": f"{first_name}'s {month_name} Story",
        "story": story_body,
        "word_count": len(story_body.split())
    }


def generate_monthly_change_summary(db: Session, child_id: uuid.UUID, month_str: Optional[str] = None) -> List[str]:
    """Generates the monthly change summary comparing this month to last month."""
    current = generate_monthly_snapshot(db, child_id, month_str)

    if month_str:
        year, month = map(int, month_str.split("-"))
    else:
        now = datetime.utcnow()
        year, month = now.year, now.month

    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    prev_month_str = f"{prev_year:04d}-{prev_month:02d}"

    previous = generate_monthly_snapshot(db, child_id, prev_month_str)

    summaries = []

    # 1. Compare domains count
    curr_domains = current["domains"]
    prev_domains = previous["domains"]

    for domain_key in curr_domains:
        curr_val = curr_domains.get(domain_key, 0)
        prev_val = prev_domains.get(domain_key, 0)
        domain_name = domain_key.replace("_", " ").capitalize()

        if curr_val > prev_val + 1:
            summaries.append(f"↑ More {domain_name.lower()} moments were captured this month")
        elif curr_val < prev_val - 1:
            summaries.append(f"↓ Fewer {domain_name.lower()} moments were logged")
        else:
            if curr_val > 0:
                summaries.append(f"→ {domain_name} observations remained steady")

    # 2. Compare milestones
    curr_ms_count = len(current["milestones_achieved"])
    prev_ms_count = len(previous["milestones_achieved"])

    if curr_ms_count > prev_ms_count:
        if curr_ms_count - prev_ms_count == 1:
            summaries.append("↑ One new milestone was observed")
        else:
            summaries.append(f"↑ {curr_ms_count - prev_ms_count} new milestones were achieved")
    elif curr_ms_count < prev_ms_count and curr_ms_count > 0:
        summaries.append("↓ Fewer milestone achievements logged")

    # 3. Compare concerns
    curr_concerns = len(current["persistent_concerns"]) + len(current["new_concerns"])
    prev_concerns = len(previous["persistent_concerns"]) + len(previous["new_concerns"])

    if curr_concerns > prev_concerns:
        summaries.append("↑ Additional moments of communication frustration logged")
    elif curr_concerns < prev_concerns and curr_concerns > 0:
        summaries.append("↓ Fewer moments of frustration reported")
    elif curr_concerns == prev_concerns and curr_concerns > 0:
        summaries.append("→ Frustration moments continued to be monitored")

    if not summaries:
        summaries.append("→ Overall observation volume and patterns remained stable compared to last month")

    return summaries


def generate_monthly_questions(db: Session, child_id: uuid.UUID) -> List[str]:
    """Generates 3-5 curious age-aware and blind-spot aware prompts."""
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        return []
    age_months = (datetime.utcnow().date() - child.date_of_birth).days // 30

    from app.services.focus_detection_service import detect_blind_spots
    observations = db.query(Observation).filter(
        Observation.child_id == child_id,
        Observation.deleted_at.is_(None)
    ).all()
    blind_spots = detect_blind_spots(db, child_id, observations)

    questions = []

    # 1. Gather age-specific questions
    for (low, high), age_q in AGE_SPECIFIC_QUESTIONS.items():
        if low <= age_months <= high:
            questions.extend(age_q)
            break
    if not questions:
        questions.extend(AGE_SPECIFIC_QUESTIONS[(37, 120)])

    # 2. Mix in blind spot questions if available
    for bs in blind_spots:
        domain = bs["domain_name"]
        prompts = DOMAIN_PROMPTS.get(domain, [])
        if prompts:
            questions.insert(0, prompts[0])

    # 3. Filter unique questions and return 3 to 5
    unique_questions = []
    for q in questions:
        if q not in unique_questions:
            unique_questions.append(q)

    return unique_questions[:4]
