# -*- coding: utf-8 -*-
"""赛博神棍 tool 基类：统一排盘输出与可选 AI 解读。

子类实现 ``_cast``：解析参数 → 调 ``methods.xxx.calculate(...)`` → 生成排盘摘要，
返回 ``(result, summary)``。基类 ``_invoke`` 负责统一编排：

    解析参数 + 排盘（子类 _cast）→ 按需解读（_maybe_interpret）→ 统一输出（_emit）

排盘异常不炸节点：转成文本消息 + 完整的 4 个输出变量（result 里带 error 字段）。
解读失败不阻断排盘（F7）：排盘结果照常返回，note 里注明失败原因。
"""

from collections.abc import Generator
from datetime import date, datetime
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


def _to_jsonable(value):
    """把 result 里的 datetime 等转成可 JSON 序列化的值（字段名不动，R3）。"""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(item) for item in value]
    return value


class BaseOracleTool(Tool):
    METHOD_KEY = ""          # 子类覆盖：interpret.py 的方法枚举
    METHOD_NAME = ""         # 子类覆盖：中文名，写进 result["method"]

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        try:
            result, summary = self._cast(tool_parameters)
        except Exception as e:
            result = {"method": self.METHOD_NAME, "error": str(e)}
            summary = f"[排盘失败] {type(e).__name__}: {e}"
            yield from self._emit(result, summary, "")
            return
        yield from self._run_and_emit(tool_parameters, result, summary)

    def _cast(self, tool_parameters: dict[str, Any]) -> tuple[dict, str]:
        """子类实现：解析参数 → 调 methods.xxx.calculate(...) → 生成排盘摘要。"""
        raise NotImplementedError

    def _run_and_emit(self, tool_parameters, result, summary):
        """排盘完成后统一收尾：按需解读 → 拼接 note → 输出全部消息。"""
        question = tool_parameters.get("question") or ""
        interpretation, note = self._maybe_interpret(tool_parameters, result, question)
        if note:
            summary = f"{summary}\n\n{note}"
        yield from self._emit(result, summary, interpretation)

    def _emit(self, result: dict, summary: str, interpretation: str):
        result = _to_jsonable(result)
        yield self.create_variable_message("method", self.METHOD_NAME)
        yield self.create_variable_message("summary", summary)
        yield self.create_variable_message("result", result)
        yield self.create_variable_message("interpretation", interpretation or "")
        yield self.create_json_message(result)
        text = summary + ("\n\n" + interpretation if interpretation else "")
        yield self.create_text_message(text)

    def _maybe_interpret(
        self, tool_parameters, result, question
    ) -> tuple[str, str]:
        """返回 (interpretation, note)。解读失败不影响排盘。"""
        if tool_parameters.get("interpret") is False:
            return "", ""
        model_cfg = tool_parameters.get("model")
        if not model_cfg:
            return "", "[未选择模型，已跳过 AI 解读]"
        try:
            from utils.interpret import interpret
            text = interpret(self, model_cfg, self.METHOD_KEY, result, question)
            return text, ""
        except Exception as e:
            return "", f"[解读失败] {type(e).__name__}: {e}"
