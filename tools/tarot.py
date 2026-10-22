# -*- coding: utf-8 -*-
"""塔罗牌 tool：抽牌排盘 + 可选 AI 解读。"""

from datetime import datetime
from typing import Any

from methods.tarot import calculate as calculate_tarot
from tools import base
from utils.clock import now_from


SPREAD_MAP = {
    "single_card": "单张卡",
    "three_card": "三张牌阵",
    "celtic_cross": "凯尔特十字阵",
}


class TarotTool(base.BaseOracleTool):
    METHOD_KEY = "tarot"
    METHOD_NAME = "塔罗牌"

    def _cast(self, tool_parameters: dict[str, Any]) -> tuple[dict, str]:
        spread_value = tool_parameters.get("spread") or "three_card"
        spread_name = SPREAD_MAP.get(spread_value, "三张牌阵")
        seed = tool_parameters.get("seed") or None
        question = tool_parameters.get("question") or ""
        if not question:
            question = "一般指引"

        dt = now_from(self, tool_parameters)
        result = calculate_tarot(dt, question, seed=seed, spread_name=spread_name)
        lines = [f"牌阵：{result['spread_name']}"]
        for c in result["cards"]:
            orientation = "正位" if c["upright"] else "逆位"
            suit_tag = ""
            if c["type"] == "minor":
                suit_tag = f"  [{c['suit_name']}·{c['element']}]"
            meaning = c["meaning_upright"] if c["upright"] else c["meaning_reversed"]
            lines.append(
                f"[{c['position']}] {c['name']} ({c['name_en']})  {orientation}{suit_tag}"
            )
            lines.append(f"      {meaning}")
        summary = "\n".join(lines)
        return result, summary
