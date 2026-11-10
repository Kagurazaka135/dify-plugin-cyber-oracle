# -*- coding: utf-8 -*-
"""自动选法 tool：按问题挑选最合适的占卜方法，再按该方法的提示词解读。"""

from collections.abc import Generator
from typing import Any

from methods.router import route
from tools import base
from utils.casting import CASTERS, cast


class AutoRouteTool(base.BaseOracleTool):
    METHOD_KEY = "plum_blossom"   # 兜底值；实际按路由结果覆盖
    METHOD_NAME = "自动选法"

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator:
        question = tool_parameters.get("question") or ""
        decision = route(question)

        try:
            result, summary = cast(self, decision["key"], tool_parameters)
        except Exception as e:
            result = {"method": "自动选法", "routing": decision, "error": str(e)}
            summary = (
                f"[自动选法 → {decision['name']}] 排盘失败：{type(e).__name__}: {e}"
            )
            yield from self._emit(result, summary, "")
            return

        # 解读要走被选中方法自己的提示词，不能固定成梅花易数
        self.METHOD_KEY = decision["key"]
        self.METHOD_NAME = CASTERS[decision["key"]][1]
        result["routing"] = decision

        summary = f"[自动选法] {decision['name']} —— {decision['reason']}\n\n{summary}"
        yield from self._run_and_emit(tool_parameters, result, summary)
