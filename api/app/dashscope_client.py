import json
import re

import httpx
from fastapi import HTTPException, status

from .config import Settings
from .schemas import AI_CATEGORY_LABELS, AiCategory

DRINK_BRANDS = [
    "古茗",
    "沪上阿姨",
    "瑞幸",
    "喜茶",
    "奈雪的茶",
    "蜜雪冰城",
    "茶百道",
    "一点点",
    "霸王茶姬",
    "茶颜悦色",
    "阿嬷手作",
    "茉莉奶白",
    "快乐柠檬",
    "厝内小眷村",
    "鹿角巷",
    "一芳水果茶",
    "益禾堂",
    "甜啦啦",
    "7分甜",
    "椿风",
    "乐乐茶",
    "伏小桃",
    "和气桃桃",
    "茶理宜世",
    "茶话弄",
    "霓裳茶舞",
    "爷爷泡的茶",
    "圆真真",
    "兵之王",
    "新时沏",
    "黑泷堂",
    "珍煮丹",
    "丸摩堂",
    "陈多多",
    "吾饮良品",
    "茶屿水果茶",
    "挞柠",
    "柠檬向右",
    "巡茶",
    "百分茶",
]


def build_prompt(category: AiCategory) -> str:
    label = AI_CATEGORY_LABELS[category]
    category_rules: dict[AiCategory, str] = {
        "food": (
            "生成 6 个适合直接比较的中文候选。必须二选一：要么 6 个全是餐厅/品牌/店名，"
            "要么 6 个全是具体菜品/食物名；同一组里不要混合品牌和菜品。"
            "不要写动作短语，例如不要写“吃火锅”“喝奶茶”，要写“火锅”“黄焖鸡”“海底捞”这类名词。"
        ),
        "play": (
            "生成 6 个具体可执行的中文候选，尽量是地点、活动或场景名，例如“密室逃脱”“电玩城”“江边散步”。"
            "不要写“出去玩”“随便逛逛”这类泛泛动作。"
        ),
        "drink": (
            "生成 6 个中文候选，只能是具体饮品品牌名，不要写品类、动作短语或自造词。"
            f"品牌风格参考：{'、'.join(DRINK_BRANDS)}。"
            "只返回可直接作为卡片的品牌名，不要写“喝奶茶”“喝咖啡”“喝果茶”这类动作或类别。"
        ),
    }
    return (
        f"你是 Pickora 的候选项生成器。请为分类“{label}”{category_rules[category]}"
        "要求：只返回 JSON 字符串数组；不要解释；不要编号；每个选项 2 到 8 个中文字符；"
        "必须正好 6 个；选项要短、具体、适合直接作为抽卡卡牌。"
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


async def generate_dashscope_options(category: AiCategory, settings: Settings) -> list[str]:
    if not settings.dashscope_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="生成服务暂未配置，可以先手动输入选项。",
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
            detail = "生成服务配置校验失败，请检查服务器环境变量。"
        else:
            detail = "生成服务暂时不可用，可以先手动输入选项。"
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="生成服务暂时不可用，可以先手动输入选项。",
        ) from exc

    data = response.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    options = parse_options(content)
    if len(options) == 6:
        return options

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="返回格式不正确，可以先手动输入选项。",
    )
