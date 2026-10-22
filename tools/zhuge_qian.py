# -*- coding: utf-8 -*-
"""诸葛神数 tool：三字报数求签 + 可选 AI 解读。"""

from typing import Any

from methods.zhuge import calculate as calculate_zhuge
from tools import base


class ZhugeQianTool(base.BaseOracleTool):
    METHOD_KEY = "zhuge_qian"
    METHOD_NAME = "诸葛神数"

    def _cast(self, tool_parameters: dict[str, Any]) -> tuple[dict, str]:
        chars = tool_parameters.get("chars")
        if not chars:
            raise ValueError("需要输入三个汉字，比如「找工作」")
        result = calculate_zhuge(str(chars))
        qd = result["qian_data"]
        inp = result["input"]
        chars_text = "".join(inp["chars"])
        strokes_info = "  ".join(
            f"{inp['chars'][i]}={inp['strokes'][i]}画"
            for i in range(len(inp["chars"]))
        )
        lines = [
            f"你报的字：{chars_text}",
            f"康熙笔画：{strokes_info}",
            "",
            f"  {'─' * 40}",
            f"  ■ 第 {result['qian_number']} 签：{qd['title']}",
            f"  {'─' * 40}",
            "",
            "  【签诗】",
        ]
        for line in qd["poem"].split("\n"):
            lines.append(f"    {line}")
        lines.append("")
        lines.append(f"  【解签】{qd['interpretation']}")
        summary = "\n".join(lines)
        return result, summary
