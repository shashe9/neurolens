import os
import json
import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.models import Child, MilestoneStatus, Observation, Milestone

GRAPH_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "knowledge",
    "knowledge_graph.json"
)

def get_knowledge_graph() -> Dict[str, Any]:
    """Loads the knowledge graph JSON file from disk."""
    if os.path.exists(GRAPH_PATH):
        try:
            with open(GRAPH_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading knowledge graph: {e}")
    
    # Simple fallback structure
    return {}

def check_prerequisites_met(db: Session, child_id: uuid.UUID, skill_key: str) -> bool:
    """
    Checks if a child has demonstrated the prerequisite skills for a given target skill.
    Prerequisites are met if:
    1. Child has achieved the milestone linked to the prerequisite skill.
    2. OR parent has logged a positive observation mentioning the prerequisite keywords.
    """
    graph = get_knowledge_graph()
    node = graph.get(skill_key)
    if not node:
        return True

    prereqs = node.get("prerequisites", [])
    if not prereqs:
        return True

    for prereq_key in prereqs:
        prereq_node = graph.get(prereq_key)
        if not prereq_node:
            continue

        # Check 1: Milestone achieved
        milestone_keywords = prereq_node.get("milestones", [])
        met_by_milestone = False
        
        # Query child achieved/observed milestones
        achieved_milestones = db.query(MilestoneStatus).join(Milestone).filter(
            MilestoneStatus.child_id == child_id,
            MilestoneStatus.status.in_(["achieved", "observed", "consistently_demonstrated"])
        ).all()

        for ms in achieved_milestones:
            title_lower = ms.milestone.title.lower()
            desc_lower = ms.milestone.description.lower()
            # If milestone title or desc matches prerequisite milestones keywords
            if any(kw.lower() in title_lower or kw.lower() in desc_lower for kw in milestone_keywords):
                met_by_milestone = True
                break
        
        if met_by_milestone:
            continue

        # Check 2: Met by logged observations
        met_by_observation = False
        observations = db.query(Observation).filter(
            Observation.child_id == child_id,
            Observation.deleted_at.is_(None)
        ).all()

        # Keywords list for observation body search
        keywords = prereq_node.get("milestones", []) + [prereq_key.replace("_", " ")]
        for obs in observations:
            obs_body = (obs.structured_body or obs.body or "").lower()
            if any(kw.lower() in obs_body for kw in keywords):
                met_by_observation = True
                break

        if not met_by_observation:
            # prerequisite is missing
            return False

    return True
