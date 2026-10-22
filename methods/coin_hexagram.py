# -*- coding: utf-8 -*-
"""金钱卦计算。爻序自下而上，数据取自 data/iching_full.json。"""

import random

from utils.data_loader import load_data


HEXAGRAM_DATA = load_data("iching_full.json")
HEXAGRAMS_BY_ARRAY = {
    tuple(hexagram["array"][:6]): hexagram for hexagram in HEXAGRAM_DATA
}

def _normalize_throw(value):
    if isinstance(value, bool):
        raise ValueError(f"无效的掷币结果：{value!r}")
    if isinstance(value, int):
        if value not in (6, 7, 8, 9):
            raise ValueError(f"掷币结果必须是 6、7、8、9 或三枚硬币字符串：{value}")
        return value
    if isinstance(value, str) and len(value) == 3 and all(c in "12" for c in value):
        return sum(2 if coin == "1" else 3 for coin in value)
    raise ValueError(f"无效的掷币结果：{value!r}")


def _hexagram_summary(hexagram):
    return {
        "id": hexagram["id"],
        "name": hexagram["name"],
        "symbol": hexagram["symbol"],
        "scripture": hexagram["scripture"],
    }


def calculate(throws: list | None = None, question: str = "", seed=None) -> dict:
    if throws is None:
        rng = random.Random(seed) if seed is not None else random
        normalized = rng.choices((6, 7, 8, 9), weights=(1, 3, 3, 1), k=6)
    else:
        if not isinstance(throws, (list, tuple)) or len(throws) != 6:
            raise ValueError("掷币结果必须恰好包含六爻")
        normalized = [_normalize_throw(value) for value in throws]

    if throws is None:
        normalized = [_normalize_throw(value) for value in normalized]

    original_array = tuple(1 if value in (7, 9) else 0 for value in normalized)
    original_hexagram = HEXAGRAMS_BY_ARRAY.get(original_array)
    if original_hexagram is None:
        raise ValueError("卦象数据中未找到对应的本卦")

    moving_lines = [
        index for index, value in enumerate(normalized, start=1)
        if value in (6, 9)
    ]
    lines = []
    for position, value in enumerate(normalized, start=1):
        line_data = original_hexagram["lines"][position - 1]
        lines.append({
            "position": position,
            "value": value,
            "yin_yang": "阳" if value in (7, 9) else "阴",
            "moving": value in (6, 9),
            "name": line_data["name"],
            "scripture": line_data["scripture"],
        })

    changed = None
    if moving_lines:
        changed_array = tuple(1 - bit if index in moving_lines else bit
                              for index, bit in enumerate(original_array, start=1))
        changed_hexagram = HEXAGRAMS_BY_ARRAY.get(changed_array)
        if changed_hexagram is None:
            raise ValueError("卦象数据中未找到对应的变卦")
        changed = _hexagram_summary(changed_hexagram)

    original = _hexagram_summary(original_hexagram)
    if len(moving_lines) == 1:
        line = lines[moving_lines[0] - 1]
        original["moving_text"] = f"{line['name']}：{line['scripture']}"

    return {
        "method": "金钱卦",
        "throws": normalized,
        "lines": lines,
        "original": original,
        "changed": changed,
        "moving_lines": moving_lines,
        "question": question,
    }
