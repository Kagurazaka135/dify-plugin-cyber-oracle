# -*- coding: utf-8 -*-
"""小六壬 tool：掌诀推演 + 可选 AI 解读。"""

from datetime import datetime
from typing import Any

from methods.xiao_liu_ren import calculate as calculate_xiao_liu_ren
from tools import base
from utils.clock import now_from


class XiaoLiuRenTool(base.BaseOracleTool):
    METHOD_KEY = "xiao_liu_ren"
    METHOD_NAME = "小六壬"

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

        result = calculate_xiao_liu_ren(dt, question)
        lunar = result["lunar"]
        steps = result["steps"]
        final = result["final"]
        names = {1: "大安", 2: "留连", 3: "速喜", 4: "赤口", 5: "小吉", 6: "空亡"}
        lines = [
            f"起卦时间（公历）：{result['dt'].strftime('%Y年%m月%d日 %H:%M')}",
            f"起卦时间（农历）：{lunar['lunar_month']}月{lunar['lunar_day']}日"
            f" {lunar['shichen_name']}时",
            "",
            "小六壬推算：",
            f"  月落：{steps['month']}（{names[steps['month']]}）",
            f"  日落：{steps['day']}（{names[steps['day']]}）",
            f"  时落：{steps['hour']}（{names[steps['hour']]}）",
            "",
            f"【{final['name']}】{final['luck']}",
            f"  掌诀：\n{final['verse']}",
        ]
        for label, key in (
            ("总断", "fortune"),
            ("事业", "career"),
            ("感情", "love"),
            ("健康", "health"),
            ("失物", "lost"),
            ("出行", "travel"),
        ):
            lines.append(f"  {label}：{final[key]}")
        summary = "\n".join(lines)
        return result, summary
