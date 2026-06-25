import json
import re

import httpx
from fastapi import HTTPException, status

from .config import Settings
from .schemas import CATEGORY_LABELS, Category


def build_prompt(category: Category) -> str:
    label = CATEGORY_LABELS[category]
    return (
        f"你是 Pickora 的候选项生成器。请为分类“{label}”生成 6 个中文短选项。"
        "要求：只返回 JSON 字符串数组；不要解释；不要编号；每个选项 2 到 8 个中文字符；"
        "选项要日常、具体、适合直接作为抽卡卡牌。"
    )


def normalize_options(values: list[str]) -> list[str]:
    options: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = str(value).strip().strip("-•0123456789.、，, ")
        if not item or item in seen:
            continue
        seen.add(item)
        options.append(item[:16])
    return options[:6]


def parse_options(content: str) -> list[str]:
    text = content.strip()
    if not text:
        return []

    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return normalize_options([str(item) for item in parsed])
    except json.JSONDecodeError:
        pass

    bracket_match = re.search(r"\[[\s\S]*\]", text)
    if bracket_match:
        try:
            parsed = json.loads(bracket_match.group(0))
            if isinstance(parsed, list):
                return normalize_options([str(item) for item in parsed])
        except json.JSONDecodeError:
            pass

    parts = re.split(r"[\n\r,，、;；|/\\\t ]+", text)
    return normalize_options(parts)


async def generate_dashscope_options(category: Category, settings: Settings) -> list[str]:
    if not settings.dashscope_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI 暂未配置，可以先手动输入选项。",
        )

    payload = {
        "model": settings.dashscope_model,
        "messages": [
            {"role": "system", "content": "你只输出符合要求的 JSON，不输出任何解释。"},
            {"role": "user", "content": build_prompt(category)},
        ],
        "temperature": 0.9,
    }

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                settings.dashscope_base_url,
                headers={
                    "Authorization": f"Bearer {settings.dashscope_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code in {401, 403}:
            detail = "AI 配置校验失败，请检查服务器环境变量。"
        else:
            detail = "AI 服务暂时不可用，可以先手动输入选项。"
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI 服务暂时不可用，可以先手动输入选项。",
        ) from exc

    data = response.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    options = parse_options(content)
    if len(options) == 6:
        return options

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="AI 返回格式不正确，可以先手动输入选项。",
    )
