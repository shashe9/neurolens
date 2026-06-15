import uuid
from datetime import datetime, date
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.models import Child, Observation, ObservationType, MilestoneStatus
from app.services.child_profile_service import build_child_profile
from app.services.knowledge_graph_service import get_knowledge_graph, check_prerequisites_met
from app.knowledge.repository import get_all_activities, get_all_guides

def generate_personalized_learning_path(db: Session, child_id: uuid.UUID) -> Dict[str, Any]:
    """
    Generates a personalized, goal-oriented 4-week developmental plan.
    Traverses the knowledge graph to pick a target goal based on prerequisites and gaps.
    """
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise ValueError("Child profile not found.")

    profile = build_child_profile(db, child_id)
    age_months = profile["age_months"]
    graph = get_knowledge_graph()

    # 1. Identify target skill based on child profile priorities (concerns, blind spots, age fit)
    target_skill = None
    fallback_skill = "joint_attention"

    candidates = []
    for skill_key in sorted(graph.keys()):
        node = graph[skill_key]
        min_age, max_age = node["age_range"]
        
        # Check if age fits (within a 6-month buffer)
        if min_age - 3 <= age_months <= max_age + 6:
            # Check prerequisites
            if check_prerequisites_met(db, child_id, skill_key):
                # Verify if not already fully achieved in milestones
                achieved = False
                milestone_kws = node.get("milestones", [])
                
                milestone_statuses = db.query(MilestoneStatus).filter(
                    MilestoneStatus.child_id == child_id,
                    MilestoneStatus.status == "achieved"
                ).all()
                for ms in milestone_statuses:
                    title_lower = ms.milestone.title.lower()
                    if any(kw.lower() in title_lower for kw in milestone_kws):
                        achieved = True
                        break
                
                if not achieved:
                    # Calculate priority score
                    score = 0
                    
                    # Perfect age band fit
                    if min_age <= age_months <= max_age:
                        score += 15
                        
                    # Blind spot / underrepresented domain matching
                    skill_domain = node.get("developmental_domain", "")
                    if skill_domain.lower() in [d.lower() for d in profile["underrepresented_domains"]]:
                        score += 25
                        
                    # Persistent concern matching
                    skill_concerns = node.get("concerns", [])
                    if any(c.lower() in [pc.lower() for pc in profile["persistent_concerns"]] for c in skill_concerns):
                        score += 50
                        
                    # Growth signal alignment
                    if any(kw.lower() in [sig.lower() for sig in profile["growth_signals"]] for kw in milestone_kws):
                        score += 10
                        
                    candidates.append((score, node))

    if candidates:
        # Sort by score descending (highest priority first)
        candidates.sort(key=lambda x: x[0], reverse=True)
        target_skill = candidates[0][1]

    if not target_skill:
        target_skill = graph.get(fallback_skill, list(graph.values())[0])

    skill_name = target_skill["skill"]
    skill_title = target_skill.get("title", skill_name.replace("_", " ").capitalize())
    domain = target_skill["developmental_domain"]

    # 2. Gather latest evidence (recent observations in this domain)
    recent_obs = db.query(Observation).filter(
        Observation.child_id == child_id,
        Observation.deleted_at.is_(None)
    ).order_by(Observation.observed_at.desc()).first()

    if recent_obs:
        current_evidence = f"From your log on {recent_obs.observed_at.strftime('%B %d')}: \"{recent_obs.body[:60]}...\""
    else:
        current_evidence = "Based on onboarding profile; no recent logs registered in this domain."

    # Establish "Why" based on concerns or general profile
    domain_display = domain.replace("_", " ").capitalize()
    child_name = child.display_first_name
    obs_count = db.query(Observation).filter(Observation.child_id == child_id, Observation.deleted_at.is_(None)).count()
    
    why_parts = [
        f"Because {child_name} is {age_months} months old and has {obs_count} logged moment(s)."
    ]
    
    if profile.get("persistent_concerns"):
        concerns_display = ", ".join(f"'{c}'" for c in profile["persistent_concerns"][:2])
        why_parts.append(f"We noted caregiver focus around {concerns_display}, prioritizing interactive {domain_display} exercises.")
    else:
        why_parts.append(f"This plan is tailored for developmental milestone enrichment in the {domain_display} domain.")
        
    if profile.get("growth_signals"):
        signals_display = ", ".join(f"'{s.replace('_', ' ').title()}'" for s in profile["growth_signals"][:2])
        why_parts.append(f"It builds upon recent progress in {signals_display}.")
    
    if domain.lower() in [d.lower() for d in profile.get("underrepresented_domains", [])]:
        why_parts.append(f"This targets {domain_display} to balance observation coverage and clear logging blind spots.")
        
    why_goal = " ".join(why_parts)

    # 3. Pull activities & guides related to the selected target skill
    all_activities = get_all_activities()
    act_ids = target_skill.get("activities", [])
    matched_activities = [a for a in all_activities if a.id in act_ids]
    
    # Ensure variety by filling with activities in the same domain
    domain_activities = [a for a in all_activities if any(d.lower() == domain.lower() for d in a.domains) and a.id not in act_ids]
    matched_activities.extend(domain_activities)
    
    # Fallback to any remaining activities to guarantee at least 3 distinct items
    if len(matched_activities) < 3:
        for a in all_activities:
            if a not in matched_activities:
                matched_activities.append(a)

    act1 = matched_activities[0]
    act2 = matched_activities[1] if len(matched_activities) > 1 else act1
    act3 = matched_activities[2] if len(matched_activities) > 2 else act2

    all_guides = get_all_guides()
    guide_ids = target_skill.get("guides", [])
    matched_guides = [g for g in all_guides if g.id in guide_ids]
    if not matched_guides:
        matched_guides = all_guides[:1]

    # 4. Generate 4-week step progression
    weeks = []
    watch_for = target_skill.get("milestones", ["New responses", "Coordinated movements"])[0]
    log_prompt = f"Did your child demonstrate {skill_title.lower()}?"

    # Week 1
    weeks.append({
        "week": 1,
        "title": f"Foundation: Introduction to {skill_title}",
        "goal": f"Establish basic interaction patterns using {skill_title.lower()}.",
        "activity": {
            "id": act1.id,
            "title": act1.title,
            "summary": act1.summary
        },
        "watch_for": f"Initial reaction and willingness to join in: {watch_for}.",
        "what_to_log": f"Log the first time they attempt this: {log_prompt}"
    })

    # Week 2
    weeks.append({
        "week": 2,
        "title": "Consistency: Guided Play Practice",
        "goal": "Build confidence through repeated guided attempts in a comfortable setting.",
        "activity": {
            "id": act2.id,
            "title": act2.title,
            "summary": f"Practice in a quiet space with minimal distraction to reinforce {skill_title.lower()}."
        },
        "watch_for": "Longer periods of engagement and coordination.",
        "what_to_log": "Note any repetitive attempts or signs of frustration."
    })

    # Week 3
    weeks.append({
        "week": 3,
        "title": "Expansion: Social Sharing",
        "goal": "Transition the skill from parent-only play into general home routines.",
        "activity": {
            "id": act3.id,
            "title": act3.title,
            "summary": act3.summary
        },
        "watch_for": f"Child looking back to check your reactions during the activity.",
        "what_to_log": "Record if child seeks your eyes or smiles after pointing/sharing."
    })

    # Week 4
    weeks.append({
        "week": 4,
        "title": "Integration: Natural Routines",
        "goal": "Observe the target skill happening organically without prompts.",
        "activity": {
            "id": act3.id,
            "title": "Daily Routine Check-in",
            "summary": "Observe natural play and spot spontaneous developmental events in daily routines."
        },
        "watch_for": "Spontaneous gestures or speech, showing independent achievement.",
        "what_to_log": "Did they do it without prompts? Create a new observation entry!"
    })

    return {
        "child_id": str(child_id),
        "target_skill": skill_name,
        "target_skill_title": skill_title,
        "domain": domain,
        "why_this_goal": why_goal,
        "current_evidence": current_evidence,
        "weeks": weeks,
        "recommended_guides": [{
            "id": g.id,
            "title": g.title,
            "summary": g.summary
        } for g in matched_guides]
    }

