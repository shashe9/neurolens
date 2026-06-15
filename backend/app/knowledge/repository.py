import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field

# =====================================================================
# Strict Schemas for Knowledge Repository Assets
# =====================================================================

class ActivitySchema(BaseModel):
    id: str
    title: str
    summary: str
    age_min: int
    age_max: int
    domains: List[str]
    skills: List[str]
    tags: List[str]
    difficulty: str
    duration_minutes: int
    materials: List[str]
    instructions: List[str]
    why_it_helps: str
    when_to_use: List[str]
    contraindications: List[str] = Field(default_factory=list)
    related_concerns: List[str] = Field(default_factory=list)
    related_guides: List[str] = Field(default_factory=list)


class GuideSchema(BaseModel):
    id: str
    title: str
    summary: str
    age_min: int
    age_max: int
    domains: List[str]
    skills: List[str]
    reading_time: int
    difficulty: str
    body_markdown: str
    related_concerns: List[str] = Field(default_factory=list)
    related_activities: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class QuestionSchema(BaseModel):
    id: str
    question: str
    age_min: int
    age_max: int
    domains: List[str]
    skills: List[str]
    purpose: str
    follow_up_prompt: str
    priority: int


# =====================================================================
# Content Seeding Data
# =====================================================================

DEFAULT_ACTIVITIES = [
    {
        "id": "ACT_001",
        "title": "Treasure Hunt Pointing Game",
        "summary": "Hide a toy and encourage pointing/shared attention to find it.",
        "age_min": 12,
        "age_max": 24,
        "domains": ["communication", "social_emotional"],
        "skills": ["pointing", "joint_attention"],
        "tags": ["play", "pointing", "shared_attention"],
        "difficulty": "Easy",
        "duration_minutes": 5,
        "materials": ["Favorite toy", "Small cup or cloth to cover"],
        "instructions": [
            "Show the child their favorite toy, then hide it under a cup or cloth while they watch.",
            "Ask, 'Where is the toy? Can you point to it?'",
            "When the child points, celebrate enthusiastically and reveal the toy.",
            "Repeat, hiding it in slightly harder locations, always encouraging pointing gestures."
        ],
        "why_it_helps": "Encourages expressive gesturing (pointing) and joint attention, which are critical precursors to functional speech.",
        "when_to_use": ["During play time", "When trying to spark gesture communication"],
        "contraindications": [],
        "related_concerns": ["limited_gesture_use"],
        "related_guides": ["GD_001"]
    },
    {
        "id": "ACT_002",
        "title": "Stack Together Challenge",
        "summary": "Build a simple block tower together to practice coordination and cooperative play.",
        "age_min": 18,
        "age_max": 36,
        "domains": ["fine_motor", "cognitive"],
        "skills": ["stacking", "cooperative_play"],
        "tags": ["fine_motor", "play", "blocks"],
        "difficulty": "Easy",
        "duration_minutes": 7,
        "materials": ["Blocks or stackable cups"],
        "instructions": [
            "Sit together with blocks on a flat surface.",
            "Stack two blocks yourself to demonstrate.",
            "Hand a block to your child and point to the top of the tower: 'Your turn! Put the block here.'",
            "Take turns adding blocks one by one to encourage cooperative interaction and control."
        ],
        "why_it_helps": "Fosters fine motor coordination (neat grasp and stabilization) alongside early turn-taking social behavior.",
        "when_to_use": ["Floor playtime", "Quiet structured activities"],
        "contraindications": [],
        "related_concerns": ["fine_motor_delays"],
        "related_guides": ["GD_002"]
    },
    {
        "id": "ACT_003",
        "title": "Point and Share Walk",
        "summary": "Observe objects during a walk and practice pointing to share interest.",
        "age_min": 12,
        "age_max": 30,
        "domains": ["communication", "social_emotional"],
        "skills": ["pointing", "joint_attention"],
        "tags": ["outdoors", "shared_attention"],
        "difficulty": "Easy",
        "duration_minutes": 10,
        "materials": ["None"],
        "instructions": [
            "Take a short walk in the yard or park.",
            "When you see something interesting (like a bird or dog), point to it, look at your child, and describe it.",
            "Wait for your child to look at the object and back at you (shared attention).",
            "Encourage them to point to things they find interesting and label them together."
        ],
        "why_it_helps": "Builds joint attention patterns by naturally encouraging your child to coordinate their gaze between you and external objects.",
        "when_to_use": ["During daily walks", "Outdoors"],
        "contraindications": [],
        "related_concerns": ["limited_joint_attention"],
        "related_guides": ["GD_001"]
    }
]

DEFAULT_GUIDES = [
    {
        "id": "GD_001",
        "title": "Understanding Joint Attention",
        "summary": "Learn what joint attention is, why it matters, and how to spot it during daily routines.",
        "age_min": 12,
        "age_max": 36,
        "domains": ["communication", "social_emotional"],
        "skills": ["joint_attention"],
        "reading_time": 4,
        "difficulty": "Beginner",
        "body_markdown": "### What is Joint Attention?\n\nJoint attention is the shared focus of two individuals on an object. It occurs when one person alerts another to a stimulus using nonverbal cues, such as pointing, showing, or eye gaze coordination.\n\n### Why it Matters\n\nJoint attention is a critical foundation for language development, social sharing, and cooperative play. By looking back and forth between you and an object, your child is learning to coordinate intentions and communicate without words.\n\n### How to Encourage It\n\n- Follow your child's lead: look at what they are looking at and comment on it.\n- Bring objects close to your eyes to encourage eye-contact before showing them.",
        "related_concerns": ["limited_joint_attention"],
        "related_activities": ["ACT_001", "ACT_003"],
        "tags": ["education", "communication", "milestones"]
    },
    {
        "id": "GD_002",
        "title": "Supporting Early Fine Motor Skills",
        "summary": "Tips on how to use common household items to build finger strength and neat grasps.",
        "age_min": 18,
        "age_max": 36,
        "domains": ["fine_motor"],
        "skills": ["neat_grasp", "stacking"],
        "reading_time": 5,
        "difficulty": "Beginner",
        "body_markdown": "### Finger Strength and Dexterity\n\nFine motor skills involve the coordination of small muscles in movements involving the hands and fingers. Building these skills prepares children for writing, using utensils, and self-care.\n\n### Daily Activities to Try\n\n- **Scribbling**: Offer crayons or finger paint on large paper surfaces.\n- **Pincer Play**: Have your child pick up safe, small dry cereal bits using only their index finger and thumb.",
        "related_concerns": ["fine_motor_delays"],
        "related_activities": ["ACT_002"],
        "tags": ["fine_motor", "motor_skills", "play"]
    }
]

DEFAULT_QUESTIONS = [
    {
        "id": "QS_001",
        "question": "Have you noticed your child bringing objects to show you just to share their interest?",
        "age_min": 18,
        "age_max": 24,
        "domains": ["communication", "social_emotional"],
        "skills": ["showing_objects", "joint_attention"],
        "purpose": "Screening for cooperative social-sharing gestures.",
        "follow_up_prompt": "If yes, log details of the object and child smile response.",
        "priority": 1
    },
    {
        "id": "QS_002",
        "question": "Have you noticed pretend play with simple toys, like pretending a block is a phone?",
        "age_min": 19,
        "age_max": 30,
        "domains": ["social_emotional", "cognitive"],
        "skills": ["pretend_play"],
        "purpose": "Screening for symbolic developmental reasoning.",
        "follow_up_prompt": "If yes, note down what object they used and how they played.",
        "priority": 1
    },
    {
        "id": "QS_003",
        "question": "Have you noticed your child putting two words together, like 'more milk' or 'big ball'?",
        "age_min": 18,
        "age_max": 24,
        "domains": ["communication"],
        "skills": ["expressive_speech", "two_word_phrases"],
        "purpose": "Screening for early descriptive language grammar.",
        "follow_up_prompt": "Note down the exact words your child used.",
        "priority": 1
    },
    {
        "id": "QS_004",
        "question": "Have you observed your child climbing up steps or small play structures?",
        "age_min": 18,
        "age_max": 36,
        "domains": ["gross_motor"],
        "skills": ["climbing", "balance"],
        "purpose": "Checking gross motor control progression.",
        "follow_up_prompt": "Note if they alternated feet or held on for support.",
        "priority": 2
    }
]

# =====================================================================
# Loaders and Self-Seeder Utilities
# =====================================================================

KNOWLEDGE_PATH = os.path.dirname(os.path.abspath(__file__))

def ensure_knowledge_directories():
    """Create knowledge base folders inside app/knowledge."""
    dirs = [
        "activities",
        "guides",
        "questions",
        "concerns",
        "development_domains",
        "learning_paths"
    ]
    for d in dirs:
        os.makedirs(os.path.join(KNOWLEDGE_PATH, d), exist_ok=True)

def seed_default_knowledge():
    """Write default JSON files to repository if they do not exist."""
    ensure_knowledge_directories()

    # Seed activities
    activities_file = os.path.join(KNOWLEDGE_PATH, "activities", "activities.json")
    if not os.path.exists(activities_file):
        with open(activities_file, "w") as f:
            json.dump(DEFAULT_ACTIVITIES, f, indent=2)

    # Seed guides
    guides_file = os.path.join(KNOWLEDGE_PATH, "guides", "guides.json")
    if not os.path.exists(guides_file):
        with open(guides_file, "w") as f:
            json.dump(DEFAULT_GUIDES, f, indent=2)

    # Seed questions
    questions_file = os.path.join(KNOWLEDGE_PATH, "questions", "questions.json")
    if not os.path.exists(questions_file):
        with open(questions_file, "w") as f:
            json.dump(DEFAULT_QUESTIONS, f, indent=2)


def get_all_activities() -> List[ActivitySchema]:
    """Retrieve all activities from knowledge base."""
    seed_default_knowledge()
    activities_file = os.path.join(KNOWLEDGE_PATH, "activities", "activities.json")
    try:
        with open(activities_file, "r") as f:
            data = json.load(f)
            return [ActivitySchema(**item) for item in data]
    except Exception as e:
        print(f"Error loading activities: {e}")
        return [ActivitySchema(**item) for item in DEFAULT_ACTIVITIES]


def get_all_guides() -> List[GuideSchema]:
    """Retrieve all parent educational guides from knowledge base."""
    seed_default_knowledge()
    guides_file = os.path.join(KNOWLEDGE_PATH, "guides", "guides.json")
    try:
        with open(guides_file, "r") as f:
            data = json.load(f)
            return [GuideSchema(**item) for item in data]
    except Exception as e:
        print(f"Error loading guides: {e}")
        return [GuideSchema(**item) for item in DEFAULT_GUIDES]


def get_all_questions() -> List[QuestionSchema]:
    """Retrieve all curious observation questions from knowledge base."""
    seed_default_knowledge()
    questions_file = os.path.join(KNOWLEDGE_PATH, "questions", "questions.json")
    try:
        with open(questions_file, "r") as f:
            data = json.load(f)
            return [QuestionSchema(**item) for item in data]
    except Exception as e:
        print(f"Error loading questions: {e}")
        return [QuestionSchema(**item) for item in DEFAULT_QUESTIONS]
