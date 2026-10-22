# -*- coding: utf-8 -*-
"""称骨算命 tool：骨重排盘 + 可选 AI 解读。"""

from datetime import datetime
from typing import Any

from methods.bone_weight import calculate as calculate_bone_weight
from tools import base


GENDER_MAP = {"male": "男", "female": "女", "unknown": "unknown"}


class BoneWeightTool(base.BaseOracleTool):
    METHOD_KEY = "bone_weight"
    METHOD_NAME = "称骨算命"

    def _cast(self, tool_parameters: dict[str, Any]) -> tuple[dict, str]:
        birth_date = tool_parameters.get("birth_date")
        if not birth_date:
            raise ValueError("缺少出生日期 birth_date（YYYY-MM-DD）")
        dt = datetime.strptime(str(birth_date), "%Y-%m-%d")
        hour = tool_parameters.get("birth_hour")
        if hour is not None:
            hour = int(hour)
            if not 0 <= hour <= 23:
                raise ValueError("出生小时必须在 0 到 23 之间")
            dt = dt.replace(hour=hour, minute=0, second=0, microsecond=0)
        else:
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        gender_value = tool_parameters.get("gender") or "unknown"
        gender = GENDER_MAP.get(gender_value, "unknown")

        result = calculate_bone_weight(dt, gender)
        lunar = result["lunar"]
        w = result["weights"]
        lines = [
            f"出生时间（公历）：{result['birth_dt'].strftime('%Y年%m月%d日 %H:%M')}",
            f"出生时间（农历）：{lunar['year_ganzhi']}年{lunar['lunar_month']}月"
            f"{lunar['lunar_day']}日 {lunar['shichen_name']}时",
            f"性别：{result['gender']}",
            "",
            f"  年柱（{lunar['year_ganzhi']}）:  {w['year']}钱",
            f"  月柱（{lunar['lunar_month']}月）:  {w['month']}钱",
            f"  日柱（{lunar['lunar_day']}日）:   {w['day']}钱",
            f"  时柱（{lunar['shichen_name']}时）:  {w['hour']}钱",
            f"  {'─' * 18}",
            f"  总骨重：{result['bone_weight']}",
            "",
            "  称骨歌批语：",
        ]
        for line in result["poem"].split("\n"):
            lines.append(f"  {line}")
        summary = "\n".join(lines)
        return result, summary
