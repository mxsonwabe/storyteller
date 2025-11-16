import json
import uuid
from datetime import datetime
from typing import Any, Dict, List

from jsonschema import Draft202012Validator, ValidationError

from models import CoverPage, HighlightPage, InfoPage, Page, StoryPack

INPUT_DATA = "data/match_events.json"
SCHEMA_DEFINITION = "schema/story.schema.json"
WEIGHTS_FILE = "weights.example.json"

# This map translates the 'type' from match_events.json (schema)
# into the event key used in weights.example.json.
# This is necessary because the names don't always match.
TYPE_TO_WEIGHT_KEY_MAP = {
    "goal": "goal",
    "penalty goal": "goal",          # Treat as a goal
    "penalty lost": "penalty_missed", # 'penalty lost' in schema
    "attempt saved": "shot_on_target",
    "attempt blocked": "shot_on_target",
    "miss": "chance",                 # 'miss' in schema, 'chance' in weights
    "post": "chance",                 # 'post' in schema, 'chance' in weights
    "yellow card": "card_yellow",
    "red card": "card_red",           # Handle red cards if they appear
    "substitution": "substitution",
    "penalty won": "shot_on_target",  # A won penalty is a high-value event
}


def getStoryData(
    matchInfo: Dict[str, Any],
    messages: List[Dict[str, Any]],
    weights_data: Dict[str, Any],
):
    """
    Scores, ranks, and selects match events to build a list of pages.
    """
    
    event_weights: Dict[str, int] = weights_data["event_weights"]
    bonus_minute: int = weights_data["late_minute_bonus_after"]
    bonus_amount: int = weights_data["late_minute_bonus"]
    max_event_pages: int = weights_data["max_pages"]
    
    scored_events = []

    # --- 1. Score all events ---
    for msg in messages:
        msg_type = msg.get("type", "")
        minute = int(msg.get("minute", 0))

        # Find the corresponding key in the weights file
        # If not in map, use the type string itself (e.g., "corner")
        weight_key = TYPE_TO_WEIGHT_KEY_MAP.get(msg_type, msg_type)

        # Get the base score, default to 0 if not in weights
        score = event_weights.get(weight_key, 0)

        # Apply late minute bonus (only to events that have a score)
        if minute > bonus_minute and score > 0:
            score += bonus_amount

        scored_events.append((score, msg))

    # --- 2. Select top events ---
    # Sort by score (descending), using minute (desc) as a tie-breaker
    scored_events.sort(key=lambda x: (x[0], int(x[1].get("minute", 0))), reverse=True)

    # Get the top N events
    top_events_with_scores = scored_events[:max_event_pages]
    
    # Re-sort the selected events by minute (ascending) for chronological order
    top_events = [event for score, event in top_events_with_scores]
    top_events.sort(key=lambda x: int(x.get("minute", 0)))

    # --- 3. Build Pages ---
    pages: List[Page] = []
    goals_count: int = 0
    highlights_count: int = 0

    # Add the Cover Page first
    pages.append(
        CoverPage(
            type="cover",
            headline=matchInfo["description"],
            image="assets/placeholder.png",
        )
    )

    # Determine which event types should be HighlightPages
    # These are types with a score > 0 in the weights file
    highlight_weight_keys = {key for key, val in event_weights.items() if val > 0}
    
    highlight_types = set()
    for msg_type in TYPE_TO_WEIGHT_KEY_MAP:
        weight_key = TYPE_TO_WEIGHT_KEY_MAP[msg_type]
        if weight_key in highlight_weight_keys:
            highlight_types.add(msg_type)
    # Add any types that are direct matches (e.g., 'goal')
    for msg_type in event_weights:
        if event_weights[msg_type] > 0:
            highlight_types.add(msg_type)


    # Process only the selected top events
    for msg in top_events:
        msg_type: str = msg.get("type", "")
        minute: int = int(msg.get("minute", 0))
        comment: str = msg.get("comment", "")

        if msg_type in ["goal", "penalty goal"]:
            goals_count += 1

        # If the event type is in our set of "highlight" types, create a HighlightPage
        if msg_type in highlight_types:
            highlights_count += 1
            headline = ""
            
            # Create more descriptive headlines
            if msg_type in ["goal", "penalty goal"]:
                headline = f"{minute}' GOAL! -- {comment.split('.')[0]}"
            elif msg_type in ["yellow card", "red card"]:
                headline = f"{minute}' {msg_type.upper()} -- {comment.split('.')[0]}"
            elif msg_type in ["attempt saved", "attempt blocked", "post", "miss"]:
                headline = f"{minute}' CHANCE! -- {comment.split('.')[0]}"
            elif msg_type == "penalty won":
                headline = f"{minute}' PENALTY! -- {comment.split('.')[0]}"
            elif msg_type == "penalty lost":
                headline = f"{minute}' PENALTY MISSED! -- {comment.split('.')[0]}"
            else:
                 headline = f"{minute}' {msg_type.upper()} -- {comment.split('.')[0]}"

            pages.append(
                HighlightPage(
                    type="highlight",
                    headline=headline,
                    caption=comment,
                    minute=minute,
                    image="assets/placeholder.png",
                )
            )
        else:
            # Otherwise, create an InfoPage (for substitution, start, end, etc.)
            headline = f"{minute}' Match {msg_type.capitalize()}"
            pages.append(InfoPage(type="info", headline=headline, body=comment))

    metrics = {"goals": goals_count, "highlights": highlights_count}

    return pages, metrics


def createStoryPack() -> StoryPack:
    # Load weights
    try:
        with open(WEIGHTS_FILE) as f:
            weights_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Weights file not found at {WEIGHTS_FILE}")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {WEIGHTS_FILE}")
        exit(1)


    # Extract messages data
    try:
        with open(INPUT_DATA) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Match event file not found at {INPUT_DATA}")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {INPUT_DATA}")
        exit(1)
    matchInfo: Dict[str, Any] = data["matchInfo"]
    messages: List[Dict[str, Any]] = data["messages"][0]["message"]

    # Pass weights data to getStoryData
    pages, metrics = getStoryData(
        matchInfo=matchInfo, messages=messages, weights_data=weights_data
    )
    dt = str(datetime.fromisoformat(matchInfo["date"].replace("Z", "+00:00")))
    title = matchInfo.get("description")

    story_pack = StoryPack(
        title=title,
        pack_id=matchInfo.get("id", str(uuid.uuid4())),
        pages=pages,
        created_at=dt,
        metrics=metrics,
    )

    return story_pack


def main():
    print("Hello from junior-project-task!")
    print("=" * 60)
    print("Story Teller")
    print("=" * 60)
    print()
    story = createStoryPack()
    # story_pack = story.model_dump_json(indent=2)
    story_pack = story.model_dump(exclude_none=True)

    try:
        with open(SCHEMA_DEFINITION) as f:
            schema = json.load(f)
            validator = Draft202012Validator(schema)
            validator.validate(story_pack)
            print("Valid!")
            print(story.model_dump_json(indent=2))

            # Save to story.json
            output_path = "out/story.json"
            with open(output_path, "w") as out:
                json.dump(story_pack, out, indent=2)

            print(f"Saved story pack to {output_path}")
    except ValidationError as e:
        print(f"Schema Invalid: {e}")


if __name__ == "__main__":
    main()
