# -*- coding: utf-8 -*-
"""梅花易数 tool：时间卦排盘 + 可选 AI 解读。"""

from datetime import datetime
from typing import Any

from methods.plum_blossom import calculate as calculate_plum_blossom
from tools import base
from utils.clock import now_from


class PlumBlossomTool(base.BaseOracleTool):
    METHOD_KEY = "plum_blossom"
    METHOD_NAME = "梅花易数时间卦法"

    def _cast(self, tool_parameters: dict[str, Any]) -> tuple[dict, str]:
        current = now_from(self, tool_parameters)
        date_str = tool_parameters.get("date")
        hour = tool_parameters.get("hour")
        if date_str:
            dt = datetime.strptime(str(date_str), "%Y-%m-%d")
        else:
            dt = current
        if hour is not None:
            hour = int(hour)
            if not 0 <= hour <= 23:
                raise ValueError("小时必须在 0 到 23 之间")
            dt = dt.replace(hour=hour, minute=0, second=0, microsecond=0)
        elif not date_str:
            dt = current.replace(minute=0, second=0, microsecond=0)
        question = tool_parameters.get("question") or ""

        result = calculate_plum_blossom(dt, question)
        lunar = result["lunar"]
        og = result["original"]
        ch = result["changed"]
        dl = result["dynamic_line"]
        summary = (
            f"起卦时间（公历）：{lunar['datetime'].strftime('%Y年%m月%d日 %H:%M')}\n"
            f"起卦时间（农历）：{lunar['year_ganzhi']}年{lunar['lunar_month']}月"
            f"{lunar['lunar_day']}日（{lunar['day_ganzhi']}日）{lunar['shichen_name']}时\n\n"
            f"☯  本卦：{og['name']} {og['symbol']}\n"
            f"☯  变卦：{ch['name']} {ch['symbol']}\n"
            f"☯  动爻：第 {dl} 爻"
        )
        return result, summary
