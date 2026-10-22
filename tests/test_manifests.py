# -*- coding: utf-8 -*-
"""清单合规测试：manifest / provider / 7 个 tool yaml / 全仓禁词。不依赖 dify_plugin。

运行：python tests/test_manifests.py
"""

import ast
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TOOLS = [
    "plum_blossom",
    "tarot",
    "bone_weight",
    "zhuge_qian",
    "xiao_liu_ren",
    "ling_qian",
    "coin_hexagram",
]


def check_manifest():
    m = yaml.safe_load((ROOT / "manifest.yaml").read_text(encoding="utf-8"))
    assert m["type"] == "plugin"
    assert m["name"] == "cyber-oracle"
    assert m["author"] == "kagurazaka135"
    assert m["version"] == m["meta"]["version"] == "0.0.1"
    assert m["resource"]["memory"] == 268435456
    assert m["resource"]["permission"]["model"]["enabled"] is True
    assert m["resource"]["permission"]["model"]["llm"] is True
    assert m["meta"]["runner"]["version"] == "3.12"
    assert m["meta"]["runner"]["entrypoint"] == "main"
    assert set(m["label"]) >= {"en_US", "zh_Hans"}
    assert m["meta"]["runner"]["language"] == "python"


def check_provider():
    p = yaml.safe_load(
        (ROOT / "provider/cyber_oracle.yaml").read_text(encoding="utf-8")
    )
    assert p["identity"]["name"] == "cyber_oracle"
    assert len(p["tools"]) == 7
    assert p["extra"]["python"]["source"] == "provider/cyber_oracle.py"
    creds = p.get("credentials_for_provider", {})
    assert set(creds) == {"timezone"}, creds
    assert creds["timezone"]["required"] is False
    for entry in p["tools"]:
        assert pathlib.Path(ROOT / entry).is_file(), entry
    assert (ROOT / "provider/cyber_oracle.py").is_file()


def check_tools():
    for name in TOOLS:
        d = yaml.safe_load(
            (ROOT / f"tools/{name}.yaml").read_text(encoding="utf-8")
        )
        assert d["identity"]["name"] == name, (name, d["identity"]["name"])
        params = d["parameters"]
        names = {p["name"] for p in params}
        assert {"question", "model", "interpret"} <= names, (name, names)
        model = next(p for p in params if p["name"] == "model")
        assert model["type"] == "model-selector"
        assert model["scope"] == "llm"
        assert model["required"] is False
        assert model["form"] == "form"
        interpret = next(p for p in params if p["name"] == "interpret")
        assert interpret["type"] == "boolean"
        assert interpret.get("default") is True
        question = next(p for p in params if p["name"] == "question")
        assert question["form"] == "llm"
        assert d["output_schema"]["type"] == "object"
        assert set(d["output_schema"]["properties"]) == {
            "method", "summary", "result", "interpretation",
        }
        source = d["extra"]["python"]["source"]
        assert source == f"tools/{name}.py", (name, source)
        assert (ROOT / source).is_file(), source
        assert set(d["identity"]["label"]) >= {"en_US", "zh_Hans"}
        # py 能 parse
        ast.parse((ROOT / source).read_text(encoding="utf-8"))


def check_i18n():
    for name in TOOLS:
        d = yaml.safe_load((ROOT / f"tools/{name}.yaml").read_text(encoding="utf-8"))
        for p in d["parameters"]:
            assert set(p["label"]) >= {"en_US", "zh_Hans"}, (name, p["name"])
        assert set(d["description"]["human"]) >= {"en_US", "zh_Hans"}, name


def check_no_forbidden_tokens():
    # 插件运行时代码不得持有任何凭据或直连端点；scripts/ 是离线的数据生成工具，
    # 不在打包产物里，允许出现 broker 地址。
    forbidden = ["api_key", "openai", "deepseek.com", "local-broker"]
    for path in ROOT.rglob("*.py"):
        if ".venv" in path.parts or "tests" == path.parent.name or "scripts" in path.parts:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text, (path, token)
    for path in ROOT.rglob("*.yaml"):
        if ".venv" in path.parts or "scripts" in path.parts:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            assert token not in text, (path, token)


def main():
    check_manifest()
    print("OK manifest")
    check_provider()
    print("OK provider")
    check_tools()
    print("OK tools")
    check_i18n()
    print("OK i18n")
    check_no_forbidden_tokens()
    print("OK no forbidden tokens")
    print("ALL PASS")


if __name__ == "__main__":
    main()
