from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["food", "play", "movie"]

CATEGORY_LABELS: dict[Category, str] = {
    "food": "吃什么",
    "play": "去哪玩",
    "movie": "看什么剧/电影",
}


class GenerateOptionsRequest(BaseModel):
    category: Category = Field(description="Fixed category allowlist only")

    model_config = {
        "extra": "forbid",
    }


class GenerateOptionsResponse(BaseModel):
    category: Category
    options: list[str]
