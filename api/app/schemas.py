from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["food", "play", "movie", "drink"]
AiCategory = Literal["food", "play", "drink"]

CATEGORY_LABELS: dict[Category, str] = {
    "food": "吃什么",
    "play": "去哪玩",
    "movie": "看什么",
    "drink": "喝什么",
}

AI_CATEGORY_LABELS: dict[AiCategory, str] = {
    "food": CATEGORY_LABELS["food"],
    "play": CATEGORY_LABELS["play"],
    "drink": CATEGORY_LABELS["drink"],
}


class GenerateOptionsRequest(BaseModel):
    category: Category = Field(description="Fixed category allowlist only")

    model_config = {
        "extra": "forbid",
    }


class MovieOptionItem(BaseModel):
    label: str
    movieId: str | None = None
    poster: str | None = None
    type: str | None = None
    actors: str | None = None
    releaseDate: str | None = None
    score: str | None = None
    detailUrl: str | None = None


class GenerateOptionsResponse(BaseModel):
    category: Category
    options: list[str]
    items: list[MovieOptionItem] | None = None
