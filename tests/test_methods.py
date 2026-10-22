# -*- coding: utf-8 -*-
"""方法层回归测试：七种方法固定输入 + 确定性断言。不依赖 dify_plugin。

运行：python tests/test_methods.py
"""

import random
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from methods.bone_weight import calculate as calculate_bone_weight
from methods.coin_hexagram import calculate as calculate_coin_hexagram
from methods.ling_qian import calculate as calculate_ling_qian
from methods.plum_blossom import calculate as calculate_plum_blossom
from methods.tarot import calculate as calculate_tarot
from methods.xiao_liu_ren import calculate as calculate_xiao_liu_ren
from methods.zhuge import calculate as calculate_zhuge


DT = datetime(2026, 10, 22, 15, 30)


def test_plum_blossom():
    result = calculate_plum_blossom(DT, "测试")
    assert result["method"] == "梅花易数时间卦法"
    assert set(result) >= {"method", "original", "changed", "dynamic_line", "lunar"}
    assert isinstance(result["dynamic_line"], int) and 1 <= result["dynamic_line"] <= 6
    assert result["original"]["name"] and result["changed"]["name"]
    # 确定性：同一输入结果一致
    again = calculate_plum_blossom(DT, "测试")
    assert again["original"] == result["original"]
    assert again["changed"] == result["changed"]
    assert again["dynamic_line"] == result["dynamic_line"]


def test_tarot():
    result = calculate_tarot(DT, "测试", seed="abc")
    assert result["method"] == "塔罗牌"
    assert result["spread_name"] == "三张牌阵"
    assert len(result["cards"]) == 3
    for card in result["cards"]:
        assert card["name"] and isinstance(card["upright"], bool)
        assert card["position"]
    # seed 复现
    again = calculate_tarot(DT, "测试", seed="abc")
    assert [c["name"] for c in again["cards"]] == [c["name"] for c in result["cards"]]
    assert [c["upright"] for c in again["cards"]] == [c["upright"] for c in result["cards"]]
    # 默认牌阵
    assert calculate_tarot(DT, "测试")["spread_name"] == "三张牌阵"


def test_bone_weight():
    result = calculate_bone_weight(DT, "unknown")
    assert result["method"] == "称骨算命"
    weights = result["weights"]
    assert set(weights) == {"year", "month", "day", "hour", "total"}
    assert weights["total"] == (
        weights["year"] + weights["month"] + weights["day"] + weights["hour"]
    )
    assert result["bone_weight"] and result["poem"]
    # 确定性
    assert calculate_bone_weight(DT, "unknown") == result


def test_zhuge():
    result = calculate_zhuge("找工作")
    assert result["method"] == "诸葛神数"
    assert result["qian_number"] == 69  # 回归锚点（与 CLI 版一致）
    assert result["input"]["chars"] == ["找", "工", "作"]
    assert result["qian_data"]["title"] and result["qian_data"]["poem"]
    # 非汉字报错
    try:
        calculate_zhuge("zzz")
    except ValueError:
        pass
    else:
        raise AssertionError("non-Chinese input must raise ValueError")


def test_xiao_liu_ren():
    result = calculate_xiao_liu_ren(DT, "测试")
    assert result["method"] == "小六壬"
    steps = result["steps"]
    assert set(steps) == {"month", "day", "hour"}
    for value in steps.values():
        assert 1 <= value <= 6
    final = result["final"]
    for key in ("name", "luck", "verse", "fortune", "career", "love", "health", "lost", "travel"):
        assert key in final
    # 确定性
    assert calculate_xiao_liu_ren(DT, "测试")["final"] == final


def test_ling_qian():
    result = calculate_ling_qian(1)
    assert result["method"] == "灵签（关帝）"
    assert result["qian_number"] == 1
    assert result["qian_data"]["poem"]
    assert result["qian_data"]["grade"]
    # seed 复现
    numbers = {calculate_ling_qian(seed="s")["qian_number"] for _ in range(5)}
    assert len(numbers) == 1
    # 无 seed 随机分布合理
    drawn = {calculate_ling_qian()["qian_number"] for _ in range(30)}
    assert len(drawn) >= 10
    # 越界报错
    for invalid in (0, 101):
        try:
            calculate_ling_qian(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("out-of-range ling qian must raise ValueError")


def test_coin_hexagram():
    still_qian = calculate_coin_hexagram([7, 7, 7, 7, 7, 7])
    assert still_qian["method"] == "金钱卦"
    assert still_qian["original"]["name"] == "乾"
    assert still_qian["changed"] is None
    all_moving = calculate_coin_hexagram([9, 9, 9, 9, 9, 9])
    assert all_moving["changed"]["name"] == "坤"
    assert all_moving["moving_lines"] == [1, 2, 3, 4, 5, 6]
    # seed 复现
    c1 = calculate_coin_hexagram(seed="y")
    c2 = calculate_coin_hexagram(seed="y")
    assert c1["throws"] == c2["throws"]
    # 无 seed 随机仍在合法集合内
    for _ in range(50):
        assert all(v in (6, 7, 8, 9) for v in calculate_coin_hexagram()["throws"])


def main():
    tests = [
        test_plum_blossom,
        test_tarot,
        test_bone_weight,
        test_zhuge,
        test_xiao_liu_ren,
        test_ling_qian,
        test_coin_hexagram,
    ]
    for test in tests:
        test()
        print("OK", test.__name__)
    print("ALL PASS")


if __name__ == "__main__":
    main()
