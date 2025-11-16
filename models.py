from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


class CoverPage(BaseModel):
    """
    Model representing a 'cover' page in the story pack.

    Attributes:
        type (str): Must be the literal string "cover" (case-insensitive).
        headline (str): Main headline text for the cover page.
        image (str): URL or path to the cover image.
        subheadline (Optional[str]): Optional subheadline text.
    """

    type: Annotated[
        str,
        StringConstraints(
            strict=True, strip_whitespace=True, to_lower=True, pattern=r"^cover$"
        ),
    ]
    headline: str
    image: str
    subheadline: Optional[str] = None


class HighlightPage(BaseModel):
    """
    Model representing a 'highlight' page in the story pack.

    Attributes:
        type (str): Must be the literal string "highlight" (case-insensitive).
        minute (int): Minute of the event (0 to 130).
        headline (str): Short headline describing the highlight.
        caption (str): Detailed caption elaborating the highlight.
        image (Optional[str]): Optional URL or path to an image for the highlight.
        explanation (Optional[str]): Optional explanation or additional notes.
    """

    type: Annotated[
        str,
        StringConstraints(
            strict=True, strip_whitespace=True, to_lower=True, pattern="^highlight$"
        ),
    ]
    minute: Annotated[int, Field(strict=True, ge=0, le=130)]
    headline: str
    caption: str
    image: Optional[str] = None
    explanation: Optional[str] = None


class InfoPage(BaseModel):
    """
    Model representing an 'info' page in the story pack.

    Attributes:
        type (str): Must be the literal string "info" (case-insensitive).
        headline (str): Headline text for the info page.
        body (Optional[str]): Optional detailed body text.
    """

    type: Annotated[
        str,
        StringConstraints(
            strict=True, strip_whitespace=True, to_lower=True, pattern=r"^info$"
        ),
    ]
    headline: str
    body: Optional[str] = None


# Union type for polymorphic page entries
Page = Union[CoverPage, HighlightPage, InfoPage]


class StoryPack(BaseModel):
    """
    Model representing the entire story pack containing multiple pages and metadata.

    Attributes:
        pack_id (str): Unique identifier for the story pack, non-empty string.
        title (str): Title of the story pack, non-empty string.
        source (str): Source location or reference for the story pack data, non-empty string.
        pages (List[Page]): List of story pages; must contain at least one page.
        created_at (datetime): Timestamp when the story pack was created.
        metrics (Optional[Dict[str, Any]]): Optional metrics or statistics related to the story.
    """

    model_config = ConfigDict(extra="forbid")

    pack_id: Annotated[str, StringConstraints(strict=True, min_length=1)]
    title: Annotated[str, StringConstraints(strict=True, min_length=1)]
    source: Annotated[str, StringConstraints(strict=True, min_length=1)] =  "data/match_events.json"
    pages: List[Page] = Field(..., min_length=1)
    created_at: str 
    metrics: Optional[Dict[str, Any]] = None
