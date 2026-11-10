# -*- coding: utf-8 -*-
"""自动选法 / 一卦三问 tool 的离线功能测试。

用假的 runtime / session 驱动 tool，不连 Dify、不发网络请求。
运行：.venv/Scripts/python.exe tests/test_combo_tools.py
"""

import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dify_plugin.entities.tool import InvokeMessage

from methods.router import route
from tools.auto_route import AutoRouteTool
from tools.multi_cast import MultiCastTool
from utils.casting import METHOD_LABELS


FAKE_MODEL = {
    "provider": "langgenius/deepseek/deepseek",
    "model": "deepseek-flash",
    "mode": "chat",
}


class FakeRuntime:
    credentials = {}


class FakeModel:
    def __init__(self):
        self.calls = []

    def invoke(self, model_config, prompt_messages, **kwargs):
        self.calls.append(prompt_messages)
        return SimpleNamespace(
            message=SimpleNamespace(content=f"解读{len(self.calls)}")
        )


class FakeSession:
    def __init__(self):
        self.model = SimpleNamespace(llm=FakeModel())


def run(tool, params):
    """收集 tool 输出，返回 (变量字典, 文本, JSON)。"""
    variables, texts, jsons = {}, [], []
    for message in tool._invoke(params):
        if message.type == InvokeMessage.MessageType.VARIABLE:
            variables[message.message.variable_name] = message.message.variable_value
        elif message.type == InvokeMessage.MessageType.TEXT:
            texts.append(message.message.text)
        elif message.type == InvokeMessage.MessageType.JSON:
            jsons.append(message.message.json_object)
    return variables, "\n".join(texts), jsons


def check_router():
    cases = {
        "我钱包丢了怎么办": "xiao_liu_ren",
        "下周出差路上会不会顺利": "ling_qian",
        "该不该跟他分手": "tarot",
        "这一笔投资能不能赚": "coin_hexagram",
        "这个 offer 要不要接": "plum_blossom",
        "今天天气不错啊": "plum_blossom",
    }
    for question, expected in cases.items():
        decision = route(question)
        assert decision["key"] == expected, (question, decision)
        assert decision["reason"]


def check_auto_route():
    tool = AutoRouteTool(FakeRuntime(), FakeSession())
    variables, text, jsons = run(tool, {"question": "我钱包丢了怎么办"})

    assert variables["method"] == "小六壬"
    assert variables["result"]["routing"]["key"] == "xiao_liu_ren"
    assert "自动选法" in variables["summary"]
    assert "小六壬" in variables["summary"]
    assert "小六壬推算" in variables["summary"]
    assert text and jsons

    # 没选模型时只排盘，并说明跳过了解读
    assert variables["interpretation"] == ""
    assert "未选择模型" in variables["summary"]


def check_auto_route_tarot():
    tool = AutoRouteTool(FakeRuntime(), FakeSession())
    variables, _, _ = run(tool, {"question": "我喜欢的人会不会喜欢我"})
    assert variables["method"] == "塔罗牌"
    assert "牌阵：" in variables["summary"]


def check_auto_route_bad_params():
    tool = AutoRouteTool(FakeRuntime(), FakeSession())
    variables, _, _ = run(tool, {"question": "投资能不能赚", "throws": "bad"})
    # 金钱卦参数非法 → 排盘失败也要有可读输出，不能抛异常
    assert "排盘失败" in variables["summary"]
    assert variables["result"].get("error")


def check_multi_cast_without_model():
    tool = MultiCastTool(FakeRuntime(), FakeSession())
    variables, text, jsons = run(tool, {"question": "这一笔投资能不能赚"})

    assert variables["method"] == "一卦三问"
    assert variables["result"]["order"] == ["plum_blossom", "xiao_liu_ren", "tarot"]
    assert set(variables["result"]["casts"]) == set(variables["result"]["order"])
    for key in ("plum_blossom", "xiao_liu_ren", "tarot"):
        assert f"【{METHOD_LABELS[key]}】" in variables["summary"]
    assert variables["interpretation"] == ""
    assert "未选择模型" in variables["summary"]
    assert text and jsons


def check_multi_cast_include_coin():
    tool = MultiCastTool(FakeRuntime(), FakeSession())
    variables, _, _ = run(
        tool, {"question": "这一笔投资能不能赚", "include_coin": True}
    )
    assert variables["result"]["order"] == [
        "plum_blossom", "xiao_liu_ren", "tarot", "coin_hexagram",
    ]
    assert "金钱卦" in variables["summary"]


def check_multi_cast_with_model():
    session = FakeSession()
    tool = MultiCastTool(FakeRuntime(), session)
    variables, _, _ = run(
        tool, {"question": "这一笔投资能不能赚", "model": FAKE_MODEL}
    )
    # 三份分路解读 + 一次汇总 = 4 次模型调用
    assert len(session.model.llm.calls) == 4
    assert variables["interpretation"].startswith("【三卦汇总】")
    for key in ("plum_blossom", "xiao_liu_ren", "tarot"):
        assert f"【{METHOD_LABELS[key]}】" in variables["interpretation"]


def check_multi_cast_interpret_off():
    session = FakeSession()
    tool = MultiCastTool(FakeRuntime(), session)
    variables, _, _ = run(
        tool,
        {"question": "这一笔投资能不能赚", "model": {"x": 1}, "interpret": False},
    )
    assert session.model.llm.calls == []
    assert variables["interpretation"] == ""


def check_model_config_normalization():
    """Dify 传给插件的 model 值形态不固定，必须都能解开。"""
    from utils.interpret import normalize_model_config as normalize

    raw = {
        "provider": "langgenius/deepseek/deepseek",
        "model": "deepseek-flash",
        "mode": "chat",
    }
    expected = dict(raw, model_type="llm", completion_params={})
    assert normalize(raw) == expected
    assert normalize({"type": "constant", "value": raw}) == expected
    assert normalize(str({"type": "constant", "value": raw})) == expected
    assert normalize(None) is None
    assert normalize({"type": "constant", "value": None}) is None
    assert normalize({}) is None


def check_strip_reasoning():
    """推理模型的 <think> 段不能漏到展示里，但也不能把正文一起吃光。"""
    from utils.interpret import strip_reasoning

    assert strip_reasoning("正文") == "正文"
    assert strip_reasoning("<think>思考</think>正文") == "正文"
    assert strip_reasoning(
        "<think>\n<!--dify-deepseek-reasoning-->自言自语</think>\n答案"
    ) == "答案"
    # 未闭合时保留原文，宁可啰嗦也不返回空
    assert strip_reasoning("<think>未闭合\n正文") == "<think>未闭合\n正文"
    assert strip_reasoning("") == ""


def main():
    check_strip_reasoning()
    print("OK strip_reasoning")
    check_model_config_normalization()
    print("OK model config normalization")
    check_router()
    print("OK router")
    check_auto_route()
    print("OK auto_route")
    check_auto_route_tarot()
    print("OK auto_route tarot")
    check_auto_route_bad_params()
    print("OK auto_route bad params")
    check_multi_cast_without_model()
    print("OK multi_cast (no model)")
    check_multi_cast_include_coin()
    print("OK multi_cast include_coin")
    check_multi_cast_with_model()
    print("OK multi_cast (model)")
    check_multi_cast_interpret_off()
    print("OK multi_cast interpret off")
    print("ALL PASS")


if __name__ == "__main__":
    main()
