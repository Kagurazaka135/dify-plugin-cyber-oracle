# -*- coding: utf-8 -*-
"""小六壬占卜计算。"""

from datetime import datetime

from utils.data_loader import load_data
from utils.lunar import get_lunar_info


PALM_DATA = load_data("xiaoliuren.json")


def _calculate_steps(lunar_month, lunar_day, shichen_order):
    month_digit = ((lunar_month - 1) % 6) + 1
    day_digit = ((month_digit + lunar_day - 2) % 6) + 1
    final_digit = ((day_digit + shichen_order - 2) % 6) + 1
    return {"month": month_digit, "day": day_digit, "hour": final_digit}


def calculate(dt: datetime, question: str = "") -> dict:
    lunar = get_lunar_info(dt)
    steps = _calculate_steps(
        lunar["lunar_month"], lunar["lunar_day"], lunar["shichen_order"]
    )
    final = dict(PALM_DATA[str(steps["hour"])])
    final["position"] = steps["hour"]
    return {
        "method": "小六壬",
        "dt": dt,
        "lunar": lunar,
        "steps": steps,
        "final": final,
        "question": question,
    }
