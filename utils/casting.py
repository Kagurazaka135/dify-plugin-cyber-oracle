# -*- coding: utf-8 -*-
"""共用排盘：自动选法与一卦三问复用各工具自己的排盘实现。

不重写参数解析和摘要文本——直接借当前 tool 的 runtime/session 构造目标方法
的 tool 实例，调它的 ``_cast``。摘要因此和各工具单独使用时逐字一致，
不会出现「同一个方法两套说法」。
"""

from tools.coin_hexagram import CoinHexagramTool
from tools.ling_qian import LingQianTool
from tools.plum_blossom import PlumBlossomTool
from tools.tarot import TarotTool
from tools.xiao_liu_ren import XiaoLiuRenTool

# key 与 methods/router.py 的 ROUTES 保持一致
CASTERS = {
    "plum_blossom": (PlumBlossomTool, "梅花易数时间卦法"),
    "tarot": (TarotTool, "塔罗牌"),
    "xiao_liu_ren": (XiaoLiuRenTool, "小六壬"),
    "ling_qian": (LingQianTool, "灵签（关帝）"),
    "coin_hexagram": (CoinHexagramTool, "金钱卦"),
}

METHOD_LABELS = {key: label for key, (_, label) in CASTERS.items()}


def cast(tool, method_key: str, tool_parameters: dict) -> tuple[dict, str]:
    """用当前 tool 的 runtime/session 跑指定方法，返回 (result, summary)。"""
    try:
        tool_class, _ = CASTERS[method_key]
    except KeyError:
        raise ValueError(f"未知的占卜方法：{method_key}")
    helper = tool_class(tool.runtime, tool.session)
    return helper._cast(tool_parameters)
