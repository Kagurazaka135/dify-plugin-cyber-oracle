# -*- coding: utf-8 -*-
"""农历转换与干支计算工具"""

from datetime import datetime
from zhdate import ZhDate

# 天干
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
# 地支
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def get_shichen_order(hour: int) -> int:
    """根据24小时制的整点数，计算时辰地支序数（子=1, 丑=2, ..., 亥=12）"""
    shifted = (hour + 1) % 24
    return (shifted // 2) % 12 + 1


def get_year_branch_order(lunar_year: int) -> int:
    """根据农历年份计算年地支序数（子=1, 丑=2, ..., 亥=12）"""
    return ((lunar_year - 4) % 12) + 1


def get_day_ganzhi(gregorian_date: datetime) -> str:
    """根据公历日期计算日干支（用于展示）"""
    # 以 1900-01-01 甲戌日为基准
    base_date = datetime(1900, 1, 1)
    diff = (gregorian_date - base_date).days
    stem_index = diff % 10
    branch_index = diff % 12
    return HEAVENLY_STEMS[stem_index] + EARTHLY_BRANCHES[branch_index]


def get_lunar_info(dt: datetime) -> dict:
    """
    将公历时间转换为完整农历信息。
    返回 dict 包含 lunar_year, lunar_month, lunar_day, year_ganzhi,
    shichen_order, shichen_name, day_ganzhi, hour
    """
    lunar = ZhDate.from_datetime(dt)

    lunar_year = lunar.lunar_year
    lunar_month = lunar.lunar_month
    lunar_day = lunar.lunar_day
    hour = dt.hour

    year_stem_index = (lunar_year - 4) % 10
    year_branch_index = (lunar_year - 4) % 12
    year_ganzhi = HEAVENLY_STEMS[year_stem_index] + EARTHLY_BRANCHES[year_branch_index]

    shichen_order = get_shichen_order(hour)
    shichen_name = EARTHLY_BRANCHES[shichen_order - 1]

    day_ganzhi = get_day_ganzhi(dt)

    return {
        "lunar_year": lunar_year,
        "lunar_month": lunar_month,
        "lunar_day": lunar_day,
        "year_ganzhi": year_ganzhi,
        "shichen_order": shichen_order,
        "shichen_name": shichen_name,
        "day_ganzhi": day_ganzhi,
        "hour": hour,
        "datetime": dt,
    }
