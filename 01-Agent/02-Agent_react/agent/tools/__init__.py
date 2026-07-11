from typing import Dict

from agent.types import Tool
from agent.tools import calculator, current_time, word_count


def build_default_tools() -> Dict[str, Tool]:
    return {
        "calculator": Tool(
            name="calculator",
            description="计算数学表达式，例如 21+21、100*3、(10+5)/3",
            run=calculator.run,
        ),
        "get_current_time": Tool(
            name="get_current_time",
            description="获取当前日期时间；Action Input 填时区如 Asia/Shanghai，留空则用默认时区",
            run=current_time.run,
        ),
        "word_count": Tool(
            name="word_count",
            description="统计一段文字的字符数和词数",
            run=word_count.run,
        ),
    }
