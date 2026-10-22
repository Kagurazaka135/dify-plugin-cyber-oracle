# -*- coding: utf-8 -*-
"""关帝灵签 tool：抽签 + 可选 AI 解读。"""

from typing import Any

from methods.ling_qian import calculate as calculate_ling_qian
from tools import base


class LingQianTool(base.BaseOracleTool):
    METHOD_KEY = "ling_qian"
    METHOD_NAME = "灵签（关帝）"

    def _cast(self, tool_parameters: dict[str, Any]) -> tuple[dict, str]:
        qian_number = tool_parameters.get("qian_number")
        if qian_number is not None:
            qian_number = int(qian_number)
        seed = tool_parameters.get("seed") or None
        question = tool_parameters.get("question") or ""

        result = calculate_ling_qian(qian_number, question, seed=seed)
        qian = result["qian_data"]
        lines = [
            f"■ 第 {result['qian_number']} 签：{qian['title']}：{qian['grade']}",
            "【签诗】",
        ]
        for line in qian["poem"].splitlines():
            lines.append(f"  {line}")
        lines.append("")
        lines.append(f"【断语】{qian['interpretation']}")
        summary = "\n".join(lines)
        return result, summary
