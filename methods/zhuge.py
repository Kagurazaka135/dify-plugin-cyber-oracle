# -*- coding: utf-8 -*-
"""诸葛神数占卜模块

对外唯一接口：calculate(chars) -> dict
"""

import os

from utils.data_loader import load_data


DEFAULT_QIAN = {
    "title": "签文暂缺",
    "poem": "三字通天地\n一签问古今\n吉凶皆自取\n何必问神明",
    "interpretation": "此签暂无记载，请以平常心看待。",
}


def _load_qian_data():
    """加载签文 JSON，数据缺失时保留历史兜底签逻辑。"""
    try:
        return load_data("zhuge_qian.json")
    except FileNotFoundError:
        return {}


QIAN_DATA = _load_qian_data()
KANGXI_STROKES = load_data("kangxi_strokes.json")


def _stroke_to_digit(stroke_count):
    """笔画数 % 8，余 0 取 8，返回 1-8"""
    r = stroke_count % 8
    return 8 if r == 0 else r


def calculate(chars):
    """
    诸葛神数计算入口。
    参数：
        chars: 用户输入的字符串，比如 "找工作"
    返回：
        dict: method, input, qian_number, qian_data
    """
    cleaned = "".join(chars.split())
    if len(cleaned) == 0:
        raise ValueError("至少需要输入一个汉字哦，比如'找工作'这样三个字。")

    char_list = list(cleaned)[:3]
    for c in char_list:
        if not ("一" <= c <= "鿿"):
            raise ValueError(
                f"'{c}' 看起来不是中文汉字哦。请输入三个汉字，比如'找工作'。"
            )

    strokes = []
    for c in char_list:
        if c not in KANGXI_STROKES:
            raise ValueError(f"'{c}' 不在康熙笔画字典里")
        strokes.append(KANGXI_STROKES[c])

    while len(strokes) < 3:
        strokes.append(0)

    hundreds = _stroke_to_digit(strokes[0])
    tens = _stroke_to_digit(strokes[1])
    ones = _stroke_to_digit(strokes[2])
    qian = hundreds * 100 + tens * 10 + ones

    while qian > 384:
        qian -= 384
    if qian <= 0:
        qian = 1

    qian_data = dict(QIAN_DATA.get(str(qian), DEFAULT_QIAN))
    if not all(key in qian_data for key in ("title", "poem", "interpretation")):
        qian_data = {
            **DEFAULT_QIAN,
            **qian_data,
        }

    return {
        "method": "诸葛神数",
        "input": {
            "chars": char_list,
            "strokes": strokes,
        },
        "qian_number": qian,
        "qian_data": qian_data,
    }
