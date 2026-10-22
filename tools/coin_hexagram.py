# -*- coding: utf-8 -*-
"""金钱卦 tool：六爻掷币起卦 + 可选 AI 解读。"""

from typing import Any

from methods.coin_hexagram import calculate as calculate_coin_hexagram
from tools import base


class CoinHexagramTool(base.BaseOracleTool):
    METHOD_KEY = "coin_hexagram"
    METHOD_NAME = "金钱卦"

    def _cast(self, tool_parameters: dict[str, Any]) -> tuple[dict, str]:
        throws_param = tool_parameters.get("throws")
        throws = None
        if throws_param:
            tokens = [token.strip() for token in str(throws_param).split(",")]
            throws = []
            for token in tokens:
                if len(token) == 3 and all(char in "12" for char in token):
                    throws.append(token)
                else:
                    try:
                        throws.append(int(token))
                    except ValueError:
                        raise ValueError("掷币结果只能由 6/7/8/9 或三位硬币字符串组成")
        seed = tool_parameters.get("seed") or None
        question = tool_parameters.get("question") or ""

        result = calculate_coin_hexagram(throws, question, seed=seed)
        original = result["original"]
        lines = [
            f"六次掷币（自下而上）：{'、'.join(map(str, result['throws']))}",
            "",
            f"☯ 本卦：{original['name']} {original['symbol']}",
            f"  卦辞：{original['scripture']}",
        ]
        moving_lines = result["moving_lines"]
        if moving_lines:
            lines.append(f"  动爻：第 {', '.join(map(str, moving_lines))} 爻")
            for line in result["lines"]:
                if line["moving"]:
                    lines.append(f"    {line['name']}：{line['scripture']}")
            if "moving_text" in original:
                lines.append(f"  动爻爻辞：{original['moving_text']}")
        else:
            lines.append("  静卦（无动爻）")
        changed = result["changed"]
        if changed is not None:
            lines.append(f"☯ 变卦：{changed['name']} {changed['symbol']}")
            lines.append(f"  卦辞：{changed['scripture']}")
        summary = "\n".join(lines)
        return result, summary
