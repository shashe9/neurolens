import uuid
import pytest
from pydantic import ValidationError
from app.models.models import InteractionType
from app.schemas.schemas import (
    AISuggestRequest,
    AISuggestResponse,
    AIConfirmRequest,
    DomainSuggestion,
    ObservationSuggestion
)

def test_valid_ai_suggest_request():
    payload = {
        "observation_text": "Eli stacked four wooden blocks on top of each other.",
        "child_id": str(uuid.uuid4()),
        "child_age_months": 24
    }
    request = AISuggestRequest(**payload)
    assert request.observation_text == payload["observation_text"]
    assert request.child_age_months == 24

def test_invalid_ai_suggest_request_empty_text():
    with pytest.raises(ValidationError) as excinfo:
        AISuggestRequest(
            observation_text="    ",
            child_id=uuid.uuid4(),
            child_age_months=24
        )
    assert "at least 10 non-whitespace characters" in str(excinfo.value)

def test_invalid_ai_suggest_request_too_short():
    with pytest.raises(ValidationError) as excinfo:
        AISuggestRequest(
            observation_text="Too short",
            child_id=uuid.uuid4(),
            child_age_months=24
        )
    assert "at least 10 non-whitespace characters" in str(excinfo.value)

def test_invalid_ai_suggest_request_too_long():
    long_text = "a" * 1001
    with pytest.raises(ValidationError) as excinfo:
        AISuggestRequest(
            observation_text=long_text,
            child_id=uuid.uuid4(),
            child_age_months=24
        )
    assert "cannot exceed 1000 characters" in str(excinfo.value)

def test_invalid_ai_suggest_request_age_bounds():
    # Negative age
    with pytest.raises(ValidationError) as excinfo:
        AISuggestRequest(
            observation_text="Eli stacked four wooden blocks on top of each other.",
            child_id=uuid.uuid4(),
            child_age_months=-1
        )
    assert "Child age must be between 0 and 120 months" in str(excinfo.value)

    # Overly old age
    with pytest.raises(ValidationError) as excinfo:
        AISuggestRequest(
            observation_text="Eli stacked four wooden blocks on top of each other.",
            child_id=uuid.uuid4(),
            child_age_months=121
        )
    assert "Child age must be between 0 and 120 months" in str(excinfo.value)

def test_valid_ai_confirm_request():
    payload = {
        "selected_domain": "Communication",
        "selected_milestone_id": uuid.uuid4(),
        "interaction_type": InteractionType.ACCEPTED
    }
    request = AIConfirmRequest(**payload)
    assert request.interaction_type == InteractionType.ACCEPTED

def test_invalid_ai_confirm_request_enum():
    payload = {
        "selected_domain": "Communication",
        "selected_milestone_id": uuid.uuid4(),
        "interaction_type": "invalid_interaction_type_here"
    }
    with pytest.raises(ValidationError):
        AIConfirmRequest(**payload)

def test_suggestion_relevance_label_validation():
    # Valid
    sug = DomainSuggestion(domain_name="Cognitive", relevance_score=0.82, relevance_label="Strong relevance")
    assert sug.relevance_label == "Strong relevance"

    # Invalid
    with pytest.raises(ValidationError) as excinfo:
        DomainSuggestion(domain_name="Cognitive", relevance_score=0.82, relevance_label="High confidence")
    assert "Relevance label must be one of" in str(excinfo.value)
