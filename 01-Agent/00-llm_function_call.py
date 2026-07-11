# =============================================================================
#  0. 简单的 LLM Function Calling
# =============================================================================
#
#  ── Function Calling 设计框图（单问题 · 一轮工具调用）────────────────────────
#
#    用户提问（单个简单问题）
#       │
#       ▼
#    messages = [system, user] + TOOLS
#       │
#       ▼
#    LLM 第 1 次调用
#       │
#       有 tool_calls？
#       ├─ 否 ──► 直接返回文本答案
#       │
#       └─ 是
#           │
#           ▼
#       执行本地工具（TOOL_HANDLERS）
#           │
#           ▼
#       追加 [tool] 结果到 messages
#           │
#           ▼
#       LLM 第 2 次调用 ──► 返回最终答案
#
#  适用场景：一次只答一个问题，不做复合问题拆解。
#
#  工具：
#    - get_current_date  获取当前日期
#    - get_weather       查询城市天气（模拟数据）
#    - greet_person      识别人名：女孩夸赞，男孩夸游戏打得好
#
#  依赖：pip install openai python-dotenv
#  环境变量：DEEPSEEK_API_KEY（可在 Agent 子目录 .env 或本目录 .env 中配置）
#
# =============================================================================

import json
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from openai import OpenAI

sys.stdout.reconfigure(encoding="utf-8")

_DIR = os.path.dirname(os.path.abspath(__file__))
for _env in (".env", "01-Agent_react/.env", "04-LATS/.env"):
    load_dotenv(dotenv_path=os.path.join(_DIR, _env))

# 常见名字性别提示（演示用，未知名字时由 LLM 传入 gender）
_FEMALE_HINTS = {"小红", "小丽", "小美", "小芳", "Julie", "玛丽", "安娜"}
_MALE_HINTS = {"小明", "小刚", "小强", "小伟", "Tom", "Jack", "大卫"}

# ── 工具实现 ──────────────────────────────────────────────────────────────────


def get_current_date(timezone: str = "Asia/Shanghai") -> str:
    """返回指定时区的当前日期。"""
    tz = (timezone or "Asia/Shanghai").strip() or "Asia/Shanghai"
    try:
        now = datetime.now(ZoneInfo(tz))
        return now.strftime("%Y-%m-%d")
    except Exception as exc:
        return f"ERROR: invalid timezone '{tz}': {exc}"


def get_weather(city: str) -> str:
    """返回城市天气（演示用模拟数据）。"""
    city = (city or "").strip()
    if not city:
        return "ERROR: city is required"

    mock = {
        "北京": {"temp": 22, "condition": "晴", "humidity": 35},
        "上海": {"temp": 25, "condition": "多云", "humidity": 60},
        "广州": {"temp": 28, "condition": "阵雨", "humidity": 75},
        "深圳": {"temp": 27, "condition": "阴", "humidity": 70},
    }
    data = mock.get(city)
    if not data:
        return f"{city}：暂无天气数据（演示仅支持北京/上海/广州/深圳）"
    return (
        f"{city}：{data['condition']}，气温 {data['temp']}°C，"
        f"湿度 {data['humidity']}%"
    )


def _infer_gender(name: str, gender: str) -> str:
    """返回 female / male / unknown。"""
    g = (gender or "").strip().lower()
    if g in ("female", "girl", "女", "女孩", "f"):
        return "female"
    if g in ("male", "boy", "男", "男孩", "m"):
        return "male"
    if name in _FEMALE_HINTS:
        return "female"
    if name in _MALE_HINTS:
        return "male"
    return "unknown"


def greet_person(name: str, gender: str = "") -> str:
    """识别人名：女孩打印夸赞词汇，男孩夸游戏打得好。"""
    name = (name or "").strip()
    if not name:
        return "ERROR: name is required"

    inferred = _infer_gender(name, gender)
    if inferred == "female":
        msg = f"{name}，你真美丽动人、聪慧可爱、气质出众！"
    elif inferred == "male":
        msg = f"{name}，你游戏打得真棒！"
    else:
        msg = f"你好 {name}！（未能判断性别，请补充 gender 参数）"

    print(f"[tool] {msg}")
    return msg


TOOL_HANDLERS = {
    "get_current_date": get_current_date,
    "get_weather": get_weather,
    "greet_person": greet_person,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "获取指定时区的当前日期，格式 YYYY-MM-DD。",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "IANA 时区名，如 Asia/Shanghai、UTC。",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的当前天气。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名，如北京、上海。",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "greet_person",
            "description": "根据人名打招呼：女孩则夸赞她美丽聪慧，男孩则夸他游戏打得好。",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "要识别的人名，如小红、小明、Julie。",
                    },
                    "gender": {
                        "type": "string",
                        "description": "性别：female（女）或 male（男）。可根据名字推断后传入。",
                    },
                },
                "required": ["name"],
            },
        },
    },
]


# ── Function Calling 循环 ─────────────────────────────────────────────────────


def _format_messages(messages: list[dict]) -> str:
    """将 messages 格式化为可读日志。"""
    blocks = []
    for msg in messages:
        role = msg.get("role", "?")
        lines = [f"[{role}]"]
        content = msg.get("content")
        lines.append(content if content else "(无文本内容)")
        if msg.get("tool_calls"):
            lines.append("tool_calls:")
            for tc in msg["tool_calls"]:
                fn = tc.get("function", {})
                lines.append(f"  - {fn.get('name')}({fn.get('arguments')})")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _format_assistant_msg(msg) -> str:
    """格式化 LLM 返回的 assistant 消息。"""
    parts = []
    if msg.content:
        parts.append(msg.content)
    if msg.tool_calls:
        parts.append("tool_calls:")
        for tc in msg.tool_calls:
            parts.append(f"  - {tc.function.name}({tc.function.arguments})")
    return "\n".join(parts) if parts else "(无文本内容，且无 tool_calls)"


def _execute_tool(name: str, arguments: str) -> str:
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        return f"ERROR: unknown tool '{name}'"
    try:
        args = json.loads(arguments or "{}")
        return str(handler(**args))
    except Exception as exc:
        return f"ERROR: {exc}"


def _call_llm(client: OpenAI, messages: list[dict], model: str, label: str):
    """调用 LLM 并打印日志，返回 assistant message。"""
    print(f"\n{'─' * 60}")
    print(f"{label} | model={model}")
    print(">>> 请求 messages:")
    print(_format_messages(messages))
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS,
        temperature=0,
    )
    msg = response.choices[0].message
    print("<<< LLM 响应:")
    print(_format_assistant_msg(msg))
    print(f"{'─' * 60}")
    return msg


def _append_assistant(messages: list[dict], msg) -> None:
    record: dict = {"role": "assistant", "content": msg.content}
    if msg.tool_calls:
        record["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in msg.tool_calls
        ]
    messages.append(record)


def chat_with_tools(client: OpenAI, user_message: str, model: str = "deepseek-chat") -> str:
    """单问题问答：最多 1 次工具调用 + 1 次最终生成。"""
    print(f"\n[用户] {user_message}")

    messages: list[dict] = [
        {
            "role": "system",
            "content": (
                "你是一个有帮助的助手。每次只处理一个简单问题。"
                "需要实时信息时调用一次工具，然后直接回答。"
                "不要拆解复合问题，不要连续多次调用工具。"
            ),
        },
        {"role": "user", "content": user_message},
    ]

    # 第 1 次：LLM 决定直接回答，或调用工具
    msg = _call_llm(client, messages, model, "LLM 第 1 次")
    _append_assistant(messages, msg)

    if not msg.tool_calls:
        print("[结果] 无需工具，直接返回")
        return msg.content or ""

    # 执行工具，把结果写回 messages
    print(f"[工具] 调用 {len(msg.tool_calls)} 个工具")
    for tc in msg.tool_calls:
        result = _execute_tool(tc.function.name, tc.function.arguments)
        print(f"  {tc.function.name}({tc.function.arguments}) → {result}")
        messages.append(
            {"role": "tool", "tool_call_id": tc.id, "content": result}
        )

    # 第 2 次：基于工具结果生成最终答案
    final_msg = _call_llm(client, messages, model, "LLM 第 2 次")
    print("[结果] 基于工具结果返回最终答案")
    return final_msg.content or ""


def main() -> None:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError(
            "未找到 DEEPSEEK_API_KEY。请在 Agent/.env 或任一子项目 .env 中配置。"
        )

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    questions = [
        "今天是几号？",
        "跟 Julie 打个招呼。",
    ]

    print("=" * 60)
    print("LLM Function Calling 示例")
    print("可用工具：get_current_date / get_weather / greet_person")
    print("=" * 60)

    for q in questions:
        answer = chat_with_tools(client, q)
        print(f"[助手] {answer}")


if __name__ == "__main__":
    main()
