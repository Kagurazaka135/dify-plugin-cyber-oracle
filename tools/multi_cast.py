# -*- coding: utf-8 -*-
"""一卦三问 tool：同一时刻用多种方法起卦，各自解读后汇总。"""

from typing import Any

from tools import base
from utils.casting import METHOD_LABELS, cast
from utils.interpret import interpret, normalize_model_config, summarize_multi

DEFAULT_KEYS = ["plum_blossom", "xiao_liu_ren", "tarot"]
COIN_KEY = "coin_hexagram"


class MultiCastTool(base.BaseOracleTool):
    METHOD_KEY = "multi_cast"     # 不走单方法提示词，解读在这里自己编排
    METHOD_NAME = "一卦三问"

    def _invoke(self, tool_parameters: dict[str, Any]):
        question = tool_parameters.get("question") or "一般指引"
        keys = list(DEFAULT_KEYS)
        if tool_parameters.get("include_coin"):
            keys.append(COIN_KEY)

        casts = {}
        summaries = {}
        for key in keys:
            try:
                casts[key], summaries[key] = cast(self, key, tool_parameters)
            except Exception as e:
                casts[key] = {"method": METHOD_LABELS[key], "error": str(e)}
                summaries[key] = f"[排盘失败] {type(e).__name__}: {e}"

        result = {
            "method": "一卦三问",
            "question": question,
            "order": keys,
            "casts": casts,
        }
        summary = "\n\n".join(
            f"【{METHOD_LABELS[key]}】\n{summaries[key]}" for key in keys
        )

        interpretation, note = self._interpret_all(
            tool_parameters, question, keys, casts, summaries
        )
        if note:
            summary = f"{summary}\n\n{note}"

        yield from self._emit(result, summary, interpretation)

    def _interpret_all(self, tool_parameters, question, keys, casts, summaries):
        """返回 (interpretation, note)。汇总失败时三份解读照常给出。"""
        if tool_parameters.get("interpret") is False:
            return "", ""
        raw = tool_parameters.get("model")
        if normalize_model_config(raw) is None:
            return "", "[未选择模型，已跳过 AI 解读]"
        model_cfg = raw

        readings = []
        for key in keys:
            label = METHOD_LABELS[key]
            if "error" in casts[key]:
                continue
            try:
                text = interpret(self, model_cfg, key, casts[key], question)
            except Exception as e:
                text = f"(这一路解读失败：{type(e).__name__}: {e})"
            readings.append(f"【{label}】\n{text}")

        readings_text = "\n\n".join(readings)
        casts_text = "\n\n".join(
            f"【{METHOD_LABELS[key]}】\n{summaries[key]}" for key in keys
        )
        try:
            overview = summarize_multi(
                self, model_cfg, question, casts_text, readings_text
            )
            head = f"【三卦汇总】\n{overview}"
        except Exception as e:
            head = f"(汇总失败：{type(e).__name__}: {e})三份解读在下面，可以自己对照着看。"

        return f"{head}\n\n{'=' * 50}\n\n{readings_text}", ""
