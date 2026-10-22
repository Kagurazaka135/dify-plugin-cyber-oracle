# -*- coding: utf-8 -*-
"""关帝灵签计算。"""

import random

from utils.data_loader import load_data


QIAN_DATA = load_data("ling_qian_guan_di.json")


def calculate(qian_number: int | None = None, question: str = "", seed=None) -> dict:
    if qian_number is None:
        rng = random.Random(seed) if seed is not None else random
        qian_number = rng.randint(1, 100)
    if isinstance(qian_number, bool) or not isinstance(qian_number, int):
        raise ValueError("签号必须是 1 到 100 之间的整数")
    if not 1 <= qian_number <= 100:
        raise ValueError("签号必须在 1 到 100 之间")

    qian_data = QIAN_DATA.get(str(qian_number))
    if qian_data is None:
        raise ValueError(f"灵签数据中缺少第 {qian_number} 签")
    return {
        "method": "灵签（关帝）",
        "qian_number": qian_number,
        "qian_data": dict(qian_data),
        "question": question,
    }
