"""
Tests for the story pack generation logic based on invariants.md.

To run these tests:
1. Make sure you have pytest and pytest-mock:
   pip install pytest pytest-mock
2. Run pytest from the root directory:
   pytest
"""

import json
import re
import pytest
from unittest.mock import patch, MagicMock

# Import the functions to be tested from main.py
from main import getStoryData, createStoryPack, INPUT_DATA, WEIGHTS_FILE, SCHEMA_DEFINITION
from models import StoryPack

# --- Fixtures ---
# These fixtures provide mock data for the tests.

@pytest.fixture
def weights_data():
    """Provides the contents of weights.example.json."""
    return {
        "event_weights": {
            "goal": 5,
            "penalty_missed": 4,
            "shot_on_target": 3,
            "card_red": 3,
            "card_yellow": 1,
            "chance": 2,
            "substitution": 0
        },
        "late_minute_bonus_after": 75,
        "late_minute_bonus": 1,
        "max_pages": 7
    }

@pytest.fixture
def sample_match_info():
    """Provides a minimal matchInfo dictionary."""
    return {
        "id": "test-match-id",
        "description": "Test Match: Team A vs Team B",
        "date": "2025-11-10T20:00:00Z"
    }

@pytest.fixture(autouse=True)
def mock_generate_caption():
    """
    Automatically mocks the external `generate_caption` call for all tests.
    This prevents API calls and makes tests fast and deterministic.
    """
    # We patch 'main.generate_caption' because that is where it is imported and called.
    with patch('main.generate_caption') as mock_gen:
        # Return a standard placeholder asset and a descriptive mock caption
        mock_gen.return_value = ("assets/placeholder.png", "This is a mock AI caption.")
        yield mock_gen

# --- Tests ---

## 1. Invariant Tests (Happy Path)

def test_invariant_schema_validation(mock_generate_caption):
    """
    Test Invariant 1: Pack validates against schema/story.schema.json.
    
    This is an integration test that runs the full createStoryPack()
    function and validates its output against the real schema.
    It requires the data files (match_events.json, etc.) to be in place.
    """
    
    # Load the real schema
    try:
        with open(SCHEMA_DEFINITION) as f:
            schema = json.load(f)
    except FileNotFoundError:
        pytest.fail(f"Test setup error: Schema file not found at {SCHEMA_DEFINITION}")

    # Generate the story pack
    # The mock_generate_caption fixture automatically handles the API call
    story_pack_model = createStoryPack()
    
    # Dump the Pydantic model to a dict, excluding None values
    story_pack_dict = story_pack_model.model_dump(exclude_none=True)

    # Validate against the schema
    try:
        from jsonschema import Draft202012Validator
        Draft202012Validator(schema).validate(story_pack_dict)
    except ImportError:
        pytest.skip("jsonschema not installed. Skipping schema validation test.")
    except Exception as e:
        # If validation fails, this test fails
        pytest.fail(f"Output FAILED schema validation: {e}")

def test_invariant_one_cover_page_at_index_0(sample_match_info, weights_data):
    """
    Test Invariant 2: Contains exactly one cover Page at index 0.
    """
    # Use empty messages, we should still get a cover page
    messages = []
    
    pages, _ = getStoryData(sample_match_info, messages, weights_data)
    
    # Check that pages list is not empty
    assert len(pages) >= 1
    
    # Check that page 0 is a cover
    assert pages[0].type == "cover"
    assert pages[0].headline == sample_match_info["description"]
    
    # Check that no other pages are cover pages
    # (In this case, there are no other pages)
    for page in pages[1:]:
        assert page.type != "cover"

def test_invariant_ordering_is_deterministic_and_chronological(sample_match_info, weights_data):
    """
    Test Invariant 4: Ordering is stable and deterministic.
    This also tests that the final output pages are chronological.
    """
    messages = [
        {"type": "goal", "minute": "80", "comment": "Late goal"}, # Score 5 + 1 = 6
        {"type": "yellow card", "minute": "15", "comment": "Early card"}, # Score 1
        {"type": "penalty lost", "minute": "40", "comment": "Missed pen"} # Score 4
    ]
    
    # Run the function once
    pages1, _ = getStoryData(sample_match_info, messages, weights_data)
    
    # Run the function again with the same input
    pages2, _ = getStoryData(sample_match_info, messages, weights_data)
    
    # Test for determinism: Pydantic models can be compared directly
    assert pages1 == pages2
    
    # Test for chronological order in the final output (ignoring cover page)
    highlight_pages = pages1[1:]
    assert len(highlight_pages) == 3
    assert highlight_pages[0].minute == 15
    assert highlight_pages[1].minute == 40
    assert highlight_pages[2].minute == 80


## 2. Suggested & Negative Tests

def test_suggested_late_minute_bonus_ranking(sample_match_info, weights_data):
    """
    Test Suggested: Goal at 90 min ranks higher than shot at 10 min.
    """
    messages = [
        {"type": "attempt saved", "minute": "10", "comment": "Early shot"}, # Score: 3
        {"type": "goal", "minute": "90", "comment": "Late goal"}  # Score: 5 (base) + 1 (bonus) = 6
    ]
    
    # Set max_pages to 1 (plus cover) to force a selection
    weights_data["max_pages"] = 1
    
    pages, _ = getStoryData(sample_match_info, messages, weights_data)
    
    # We should have 2 pages: Cover + 1 Highlight
    assert len(pages) == 2
    
    # The single highlight page should be the 90th minute goal
    highlight = pages[1]
    assert highlight.type == "highlight"
    assert highlight.minute == 90
    assert "Late goal" in highlight.headline

def test_negative_invalid_model_fails_validation():
    """
    Test Negative: A pack missing a required field should fail.
    
    This tests the Pydantic models, not the main.py logic.
    """
    
    # Try to create a StoryPack without a required 'title'
    with pytest.raises(Exception): # Pydantic raises a ValidationError
        StoryPack(
            pack_id="123",
            source="file.json",
            pages=[], # This will also fail min_length=1
            created_at="2025-11-10T20:00:00Z"
            # 'title' is missing
        )

    # Try to create a StoryPack with an empty pages list
    with pytest.raises(Exception):
        StoryPack(
            pack_id="123",
            title="Test",
            source="file.json",
            pages=[], # Fails min_length=1
            created_at="2025-11-10T20:00:00Z"
        )
