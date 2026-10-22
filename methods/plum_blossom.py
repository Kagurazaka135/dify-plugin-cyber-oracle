# -*- coding: utf-8 -*-
"""梅花易数时间卦法模块

对外唯一接口：calculate(dt, question) -> dict
返回 dict 包含方法名、本卦、变卦、动爻、农历时间等信息
"""

from datetime import datetime
from utils.lunar import get_lunar_info, get_year_branch_order
from utils.hexagram import get_hexagram_info, compute_changed_hexagram


def _calculate_gua(year_branch: int, lunar_month: int, lunar_day: int, hour_branch: int):
    """梅花易数时间卦计算：返回 (上卦数, 下卦数, 动爻)"""
    base_sum = year_branch + lunar_month + lunar_day
    upper_num = base_sum % 8
    if upper_num == 0:
        upper_num = 8
    lower_num = (base_sum + hour_branch) % 8
    if lower_num == 0:
        lower_num = 8
    dynamic = (base_sum + hour_branch) % 6
    if dynamic == 0:
        dynamic = 6
    return upper_num, lower_num, dynamic


def calculate(dt: datetime, question: str) -> dict:
    """
    梅花易数时间卦法入口。
    参数：
        dt: 公历事件时间
        question: 用户提问（仅透传，不参与计算）
    返回：
        dict 包含本卦、变卦、动爻、农历信息等
    """
    lunar = get_lunar_info(dt)

    year_branch_order = get_year_branch_order(lunar["lunar_year"])
    upper_num, lower_num, dynamic_line = _calculate_gua(
        year_branch_order, lunar["lunar_month"], lunar["lunar_day"], lunar["shichen_order"]
    )

    original = get_hexagram_info(upper_num, lower_num)
    changed = compute_changed_hexagram(upper_num, lower_num, dynamic_line)

    return {
        "method": "梅花易数时间卦法",
        "original": original,
        "changed": changed,
        "dynamic_line": dynamic_line,
        "lunar": lunar,
        "question": question,
    }
