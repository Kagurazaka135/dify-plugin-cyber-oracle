# 任务书：赛博神棍 Dify 插件 v0.0.1

> 给 ZCode（GLM）执行。**先通读全文再动手**，按 T1 → T15 顺序做，每步做完立刻跑该步判据。
> 判据不过就停下来报告，**不要自行降级方案、不要跳过验证、不要再问设计问题**（所有决策已在下文定死）。
>
> 配套规范：同目录 `DIFY-PLUGIN-SPEC.md`（Dify 插件规范实测速查，遇到不确定的字段先查它）。

---

## 0. 施工目录（写死，不许自建）

```
G:\code\dify-plugin-cyber-oracle\
```

**素材源（只读，不改）：**

```
G:\code\赛博神棍\          # 现有 CLI 版，7 种方法的算法与数据在这里
```

**硬边界：**

- 只在上面这个施工目录里新建/修改文件，**不要在其他位置新建文件夹**。
- **`G:\code\赛博神棍\` 一个文件都不许改、不许删、不许移。** 只读复制。
- **不要 `git init`、不要 commit、不要 push、不要提 PR、不要打 tag。**
- 不安装任何全局工具；需要 Python 依赖时只在本地 venv 里装。
- 不要引入任何 LLM API Key（本插件调模型走 Dify 反向调用，见 §2 F6）。

**终端与编码提示（本机已知坑）：**

- 本机 Git Bash 把**中文参数**传给 `python -c` 时可能变成乱码。判据里出现中文路径（如 `赛博神棍`）或中文断言时：
  - 优先把判据存成 `.py` 文件再 `python 文件.py` 跑；或
  - 命令前加 `PYTHONUTF8=1`（Git Bash）——仍乱码就改用文件方式。
- 如果判据报「文件不存在」但路径里中文显示成问号或方块：**先怀疑编码，不要改代码**。
- 不要在 `python -c` 里写多层反斜杠转义（如 `replace('\\\\','/')`），层数会被 shell 吃掉。需要路径分隔符时用 `pathlib` 的 `as_posix()`。

---

## 1. 目标形态（做成什么样）

在 `G:\code\dify-plugin-cyber-oracle\` 做出一个 **Dify Tool 插件 v0.0.1**，能装进本机 Dify **1.17.1**（WSL `ubuntu-dify`，`http://localhost`）并跑通。

**一句话验收：** 新装一个 `.difypkg` → 在 Dify 里选模型、给个问题 → 7 种算命方法各自返回「排盘结果 + AI 解读」，且同一输入每次排盘一致。

**形态要点：**

- 1 个 Tool Provider（`cyber_oracle`）+ 7 个 Tool（一种方法一个 tool）。
- 排盘是**确定性纯计算**：不配置模型也能用（`interpret=false` 时零网络）。
- 解读是**可选增强**：用 Dify 工作区已配置的模型（反向调用），插件内不存 key。
- 数据/算法从 `G:\code\赛博神棍\` 复制进来，插件自包含（打包后不依赖外部目录）。

---

## 2. 特性清单（验收时逐条对照）

| 编号 | 要求 |
|---|---|
| **F1** | 目录结构符合 Dify 规范：`manifest.yaml` / `main.py` / `requirements.txt` / `.difyignore` / `_assets/` / `provider/` / `tools/`，另含 `methods/` `utils/` `data/` |
| **F2** | `manifest.yaml` 字段齐全且合法：`type: plugin`、`name: cyber-oracle`、`author: kagurazaka135`、`resource.memory: 268435456`、`meta.runner` = python **3.12** / `entrypoint: main`；顶层 `version` 与 `meta.version` 都是 `0.0.1` |
| **F3** | `resource.permission.model.enabled: true` 且 `llm: true`（反向调用必需） |
| **F4** | **7 个 tool**，名字固定：`plum_blossom`、`tarot`、`bone_weight`、`zhuge_qian`、`xiao_liu_ren`、`ling_qian`、`coin_hexagram`；每个都有 yaml + py，且都在 `provider/cyber_oracle.yaml` 的 `tools:` 列表里 |
| **F5** | 每个 tool 参数：自己的方法参数 + **必有** `model`(`model-selector`, `scope: llm`, `required: false`, `form: form`) + **必有** `interpret`(`boolean`, `default: true`, `form: form`) + **必有** `question`(`string`, `required: false`, `form: llm`)。`model` 为空或 `interpret=false` 时**只排盘不解读**，不报错 |
| **F6** | 解读只走 `self.session.model.llm.invoke(...)`，**全仓不出现** `api_key` / `OpenAI(` / `api.deepseek.com` / `local-broker` |
| **F7** | 解读失败**不阻断排盘**：LLM 异常时仍返回完整排盘结果，`interpretation` 为空字符串，并在 `text` 里注明「解读失败」及原因 |
| **F8** | 每个 tool 都通过 `create_variable_message` 输出 4 个变量：`method`(string) / `summary`(string) / `result`(object) / `interpretation`(string)；同时 `create_json_message` 输出完整结果、`create_text_message` 输出人类可读摘要 |
| **F9** | 每个 tool yaml 都有 `output_schema`，且 properties 与 F8 的 4 个变量一一对应 |
| **F10** | 数据 5 个 JSON 全部随包复制到 `data/`：`iching_full.json`、`kangxi_strokes.json`、`ling_qian_guan_di.json`、`xiaoliuren.json`、`zhuge_qian.json`；读取时全部显式 `encoding="utf-8"` |
| **F11** | `tarot` / `coin_hexagram` / `ling_qian` 支持可选 `seed` 参数（string）；传了则结果可复现，不传则保持现有随机行为 |
| **F12** | i18n：所有 yaml 的 `label` / `description` 至少有 `en_US` 与 `zh_Hans` 两套 |
| **F13** | `.difyignore` 至少挡住：`.git/`、`.env`、`__pycache__/`、`*.pyc`、`.venv/`、`*.difypkg`、`tests/`、`ZCode-*.md`、`DIFY-PLUGIN-SPEC.md` |
| **F14** | `README.md`（英文）+ `readme/README_zh_Hans.md`（中文）+ `PRIVACY.md` 齐备；README 里写明「占卜结果仅供娱乐」 |
| **F15** | 代码自包含：插件目录内不出现任何指向 `G:\code\赛博神棍\` 的路径或 `sys.path` 魔法 |
| **F16** | 打包产出 `cyber-oracle-0.0.1.difypkg`，包内**不含** `.git/` `.env` `__pycache__` `tests/` 任务书 |
| **F17** | **所有「默认当前时间」一律走 `utils.clock.local_now()`**（本地时区、已剥离 tzinfo）；`tools/` 与 `methods/` 内**禁止**出现裸 `datetime.now()` / `datetime.utcnow()` / `datetime.today()` |

### 保留清单（**回归检查用，每步动完逐条自查**）

| 编号 | 必须保持不动 |
|---|---|
| **R1** | **七种方法的计算口径与现有 `赛博神棍/` 完全一致**：同样的输入 → 同样的卦象/签号/骨重/掌诀。算法函数体除「加 seed 参数」外不许改逻辑 |
| **R2** | 数据 JSON **原样复制**，一个字符都不改（不重排、不美化、不删字段） |
| **R3** | 排盘结果 dict 的**字段名沿用现状**（`method` / `original` / `changed` / `dynamic_line` / `cards` / `weights` / `qian_data` / `final` …），不要为了"整齐"重命名 |
| **R4** | 现有 CLI 工程 `G:\code\赛博神棍\` **零改动**（本任务只读它） |
| **R5** | 解读提示词沿用 `llm_module.py` 的三段式结构（传统解读 / 白话 / 建议）+ 每套方法原有的系统提示词措辞，只把调用方式换成反向调用 |
| **R6** | 塔罗权重、金钱卦概率权重 `(1,3,3,1)`、灵签 1-100 均匀分布**不许改** |
| **R7** | 不新增任何第三方依赖，除 `dify_plugin` 与 `zhdate`（`zoneinfo` 是标准库，不算） |
| **R8** | `methods/` 与 `utils/lunar.py` `utils/hexagram.py` **一行不改**；时区处理只发生在 `utils/clock.py` → `tools/` 传参这一层。算法层永远只接收 naive datetime |

---

## 3. 施工步骤

### T1 — 建骨架 + 复制算法与数据

**做什么：**

1. 在 `G:\code\dify-plugin-cyber-oracle\` 下建目录：`_assets/` `provider/` `tools/` `methods/` `utils/` `data/` `tests/` `readme/`
2. 从 `G:\code\赛博神棍\` **复制**（不是移动）：
   - `methods/*.py` → `methods/`（`bone_weight.py` `coin_hexagram.py` `ling_qian.py` `plum_blossom.py` `tarot.py` `xiao_liu_ren.py` `zhuge.py` `__init__.py`）
   - `utils/*.py` → `utils/`（`data_loader.py` `hexagram.py` `lunar.py` `__init__.py`）
   - `data/*.json` → `data/`（5 个 JSON，外加 `SOURCES.md` 一起复制，溯源用）
3. ⚠️ **不要复制 `G:\code\赛博神棍\methods\utils\`**。它是无人引用的重复副本（与顶层 `utils/` 内容完全相同），复制进去会让插件里出现两套 `lunar.py`/`hexagram.py`，导致 import 到错的那套。插件里只保留顶层 `utils/`。
4. 复制时**排除**所有 `__pycache__/` 和 `*.pyc`。

**判据 C1：**

```bash
cd "G:/code/dify-plugin-cyber-oracle" && python -c "
import os, hashlib, json
src = r'G:/code/赛博神棍/data'
dst = r'G:/code/dify-plugin-cyber-oracle/data'
names = ['iching_full.json','kangxi_strokes.json','ling_qian_guan_di.json','xiaoliuren.json','zhuge_qian.json']
for n in names:
    a = hashlib.md5(open(os.path.join(src,n),'rb').read()).hexdigest()
    b = hashlib.md5(open(os.path.join(dst,n),'rb').read()).hexdigest()
    assert a == b, n
    print('OK', n, os.path.getsize(os.path.join(dst,n)))
print('C1 OK')
"
```

---

### T2 — main.py + manifest.yaml + requirements.txt

**做什么：**

- `main.py` **照抄**（内容一字不改）：

```python
from dify_plugin import DifyPluginEnv, Plugin

plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=120))

if __name__ == "__main__":
    plugin.run()
```

- `manifest.yaml` 按 `DIFY-PLUGIN-SPEC.md` §3 写全，值按 **F2** 固定。
- `requirements.txt`：

```
dify_plugin>=0.9.0,<0.11.0
zhdate>=0.1.6
```

**判据 C2：**

```bash
cd "G:/code/dify-plugin-cyber-oracle" && python -c "
import yaml
m = yaml.safe_load(open('manifest.yaml', encoding='utf-8'))
assert m['type'] == 'plugin'
assert m['name'] == 'cyber-oracle'
assert m['author'] == 'kagurazaka135'
assert m['version'] == m['meta']['version'] == '0.0.1'
assert m['resource']['memory'] == 268435456
assert m['resource']['permission']['model']['enabled'] is True
assert m['resource']['permission']['model']['llm'] is True
assert m['meta']['runner']['version'] == '3.12'
assert m['meta']['runner']['entrypoint'] == 'main'
assert set(m['label']) >= {'en_US','zh_Hans'}
print('C2 OK')
"
```

---

### T3 — provider yaml + py

**做什么：**

- `provider/cyber_oracle.yaml`：`identity`（author/name=`cyber_oracle`/label/description/icon/tags），**不写** `credentials_for_provider`（本插件无凭据），`tools:` 列出 7 个 yaml 路径，`extra.python.source: provider/cyber_oracle.py`。
- `provider/cyber_oracle.py`：`CyberOracleProvider(ToolProvider)`，`_validate_credentials` 直接 `pass`。

**判据 C3：**

```bash
cd "G:/code/dify-plugin-cyber-oracle" && python -c "
import yaml
p = yaml.safe_load(open('provider/cyber_oracle.yaml', encoding='utf-8'))
assert p['identity']['name'] == 'cyber_oracle'
assert len(p['tools']) == 7, p['tools']
assert p['extra']['python']['source'] == 'provider/cyber_oracle.py'
assert 'credentials_for_provider' not in p
print('C3 OK', p['tools'])
"
```

---

### T4 — 共享层适配（路径 + 编码）

**做什么（先检查，确认没问题就**不要动**）：**

1. `utils/data_loader.py` **现状已合规**：它用 `Path(__file__).resolve().parent.parent / "data"` + `encoding="utf-8"`。**保持原样，不要重写**。只需确认复制后仍能加载到 `data/`。
2. 逐个检查 `methods/*.py`：
   - `from utils.xxx import ...` 保持原样（插件内是平级包结构）。
   - 有 `print()` 的地方删掉或改成静默（插件里 print 只污染 daemon 日志）。
   - 内部 import 全部保留。
3. `methods/zhuge.py` 的 `_load_qian_data` 里那段 `os.path.dirname(os.path.dirname(__file__))` 相对定位**在插件结构下同样成立**，保持原样。只要求：`KANGXI_STROKES` 加载失败时直接抛异常（不许静默用兜底签）。

> ⚠️ 这一条的重点是**克制**：现有代码已经按"相对插件根"工作，不要为了"更好看"去重构。T4 的判据只验结果，不验写法。

**判据 C4：**

```bash
cd "G:/code/dify-plugin-cyber-oracle" && python -c "
import os, pathlib
root = pathlib.Path('.')
bad = []
for p in root.rglob('*.py'):
    if '.venv' in str(p): continue
    t = p.read_text(encoding='utf-8')
    if '赛博神棍' in t or 'G:' in t:
        bad.append(str(p))
assert not bad, bad
import pathlib
assert not pathlib.Path('methods/utils').exists(), 'methods/utils 不许复制进来'
import utils.data_loader as dl
print('data dir:', dl.DATA_DIR if hasattr(dl,'DATA_DIR') else 'n/a')
print('C4 OK')
"
```

---

### T4.5 — 时间源（**容器跑的是 UTC，不处理就会算错卦**）

**背景（以下均为实测，不是推测）：**

- `dify-plugin_daemon-1` / `dify-api-1` / `dify-web-1` 三个容器 `TZ` 为空或 UTC，容器内 `date` 显示 **UTC 时间**。
- 插件里裸写 `datetime.now()` 拿到的是 **UTC**，比北京时间**慢 8 小时**。
- Dify 的 `sys.timestamp` 只是前端声明的 `number`（unix 秒）、仅 workflow 模式可见，**不能当可靠时间源**。

**实测后果**（北京 18:22 / UTC 10:22，同一时刻）：

| 方法 | 北京时间起卦 | UTC 起卦 |
|---|---|---|
| 梅花易数 | 动爻 **3** | 动爻 **5**（卦象完全不同） |
| 小六壬 | 落位 A | 落位 B（不同） |

**另一个坑（实测）：** 带 `tzinfo` 的 **aware** datetime 传给 `zhdate` 会直接抛
`TypeError: can't subtract offset-naive and offset-aware datetimes`。
⇒ 必须**先按目标时区取时间，再剥掉 tzinfo 变成 naive**，不能直接把 aware 传进算法。

**做什么：**

新建 `utils/clock.py`：

```python
from datetime import datetime, timedelta, timezone

DEFAULT_TZ = "Asia/Shanghai"


def local_now(tz_name: str = DEFAULT_TZ) -> datetime:
    """返回目标时区的「墙上时间」，已剥离 tzinfo。

    zhdate 不接受 aware datetime，而容器默认 UTC，
    所以先按 tz 取时间、再 strip。
    """
    try:
        from zoneinfo import ZoneInfo
        aware = datetime.now(ZoneInfo(tz_name))
    except Exception:
        aware = datetime.now(timezone(timedelta(hours=8)))
    return aware.replace(tzinfo=None)
```

**然后：** T6/T7 里凡出现「默认今天 / 默认当前小时」的地方，**一律**改用 `local_now()`，**禁止**裸 `datetime.now()`。用户显式传了 `date`/`hour` 时，用用户的值构造 naive datetime（`datetime(y, m, d, h)`），不受影响。

**判据 C4.5：**

```bash
cd "G:/code/dify-plugin-cyber-oracle" && python -c "
from datetime import datetime, timezone
from utils.clock import local_now

n = local_now()
u = datetime.now(timezone.utc).replace(tzinfo=None)
assert n.tzinfo is None, 'local_now 必须返回 naive datetime'
diff = round((n - u).total_seconds() / 3600)
print('local:', n, '| utc:', u, '| 时差:', diff, '小时')
assert diff == 8, f'时区没生效，时差 {diff} 小时'

from methods import plum_blossom
r = plum_blossom.calculate(n, 'x')
print('plum with local_now:', r['original']['name'])
print('C4.5 OK')
"
```

---

### T5 — 通用解读模块 `utils/interpret.py`

**做什么：**

新建 `utils/interpret.py`，把 `G:\code\赛博神棍\llm_module.py` 里 7 套提示词搬过来，但**调用方式换成反向调用**：

- **删除**：`_get_api_key`、`_get_client`、`import openai`、`api.deepseek.com`、所有 `client.chat.completions.create`。
- **新增**统一入口：

```python
def interpret(tool, model_cfg, method_key, result, question) -> str:
    """tool 是当前 Tool 实例（提供 session），method_key 决定用哪套提示词。"""
    system, user = build_prompt(method_key, result, question)
    messages = [SystemPromptMessage(content=system), UserPromptMessage(content=user)]
    resp = tool.session.model.llm.invoke(
        model_config=model_cfg,
        prompt_messages=messages,
        stream=False,
    )
    return (resp.message.content or "").strip()
```

- `build_prompt(method_key, result, question)` 按 `llm_module.py` 里 7 个 `_interpret_*` 函数的 user prompt 构造逻辑改写，返回 `(system_prompt, user_prompt)`。
- 提示词的**三段式结构**（传统解读 / 白话 / 建议）和「赛博神棍的话，看看就行了」收尾**原样保留**（R5）。
- `method_key` 取固定枚举：`plum_blossom` `tarot` `bone_weight` `zhuge_qian` `xiao_liu_ren` `ling_qian` `coin_hexagram`。

**判据 C5：**

```bash
cd "G:/code/dify-plugin-cyber-oracle" && python -c "
import pathlib
t = pathlib.Path('utils/interpret.py').read_text(encoding='utf-8')
assert 'session.model.llm.invoke' in t
for bad in ['api_key','api.deepseek.com','import openai','OpenAI(']:
    assert bad not in t, bad
for k in ['plum_blossom','tarot','bone_weight','zhuge_qian','xiao_liu_ren','ling_qian','coin_hexagram']:
    assert k in t, k
print('C5 OK')
"
```

---

### T6 — 统一 Tool 基类 `tools/base.py`

**做什么：**

新建 `tools/base.py`，放所有 tool 共用的逻辑，**7 个 tool 都继承它**：

```python
class BaseOracleTool(Tool):
    METHOD_KEY = ""          # 子类覆盖
    METHOD_NAME = ""         # 中文名，写进 result["method"]

    def _emit(self, result: dict, summary: str, interpretation: str):
        yield self.create_variable_message("method", self.METHOD_NAME)
        yield self.create_variable_message("summary", summary)
        yield self.create_variable_message("result", result)
        yield self.create_variable_message("interpretation", interpretation or "")
        yield self.create_json_message(result)
        text = summary + ("\n\n" + interpretation if interpretation else "")
        yield self.create_text_message(text)

    def _maybe_interpret(self, tool_parameters, result, question) -> tuple[str, str]:
        """返回 (interpretation, note)。解读失败不影响排盘。"""
        if not tool_parameters.get("interpret", True):
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
```

子类实现 `_invoke`：解析参数 → 调 `methods.xxx.calculate(...)` → 生成 `summary` → 调 `_maybe_interpret` → `yield from self._emit(...)`。

**规约（每个 tool 都必须遵守）：**

- `result` 里必须带 `"method"` 字段（值 = `METHOD_NAME`）；若 `methods.xxx.calculate()` 的返回值里已经有 `method`，**用 `METHOD_NAME` 覆盖**（字段名不变，R3）。
- `summary` 是**人类可读的排盘摘要**（照 `G:\code\赛博神棍\main.py` 里对应的 `_display_*` 函数改写成"返回字符串"，不要 print）。
- 解读失败时 `summary` 后面追加 note（F7）。

**判据 C6：**

```bash
cd "G:/code/dify-plugin-cyber-oracle" && python -c "
import ast, pathlib
tree = ast.parse(pathlib.Path('tools/base.py').read_text(encoding='utf-8'))
names = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
assert 'BaseOracleTool' in names, names
print('C6 OK')
"
```

---

### T7 — 七个 tool（yaml + py）

**统一要求：**

- 文件名 = tool 名（`tools/tarot.yaml` + `tools/tarot.py`）。
- 类名 = `驼峰`（`TarotTool`），`METHOD_KEY` / `METHOD_NAME` 按表填。
- 每个 yaml 都有 `output_schema`（4 个变量，见 F9）和 `extra.python.source: tools/<name>.py`。
- **时间一律用 `from utils.clock import local_now`（见 T4.5）**：参数没填时用 `local_now()` 取「现在」，**绝不裸写 `datetime.now()`**。用户填了 `date` / `hour` 就用用户的，拼成 `datetime(y, m, d, h)`（naive，不加 tzinfo）。
- 所有 tool 的公共参数完全相同：

| 参数 | type | 必填 | form | 说明 |
|---|---|---|---|---|
| `question` | string | 否 | llm | 用户所问之事 |
| `model` | model-selector（`scope: llm`） | 否 | form | 解读用模型；不选则只排盘 |
| `interpret` | boolean（default: true） | 否 | form | 是否要 AI 解读 |

**各 tool 专属参数（照做，不要自由发挥）：**

#### T7.1 `plum_blossom` — 梅花易数

| 参数 | type | 必填 | 说明 |
|---|---|---|---|
| `date` | date | 否 | 起卦日期，`YYYY-MM-DD`，默认今天 |
| `hour` | number (0-23) | 否 | 起卦小时，默认当前小时 |

调用：`plum_blossom.calculate(dt, question)`

#### T7.2 `tarot` — 塔罗牌

| 参数 | type | 必填 | 说明 |
|---|---|---|---|
| `spread` | select | 否 | 选项 value 用英文：`single_card` / `three_card` / `celtic_cross`；默认 `three_card`。**代码内映射到中文 key**：`{"single_card":"单张卡","three_card":"三张牌阵","celtic_cross":"凯尔特十字阵"}` |
| `seed` | string | 否 | 可复现种子 |

调用：`tarot.calculate(local_now(), question, seed=seed, spread_name=...)` —— `dt` 只用于生成默认种子（`local_now()`，见 T4.5）；传了 `seed` 时以 `seed` 为准。**需要给 `tarot.calculate` 加两个可选参数**（见 T8）。

#### T7.3 `bone_weight` — 称骨算命

| 参数 | type | 必填 | 说明 |
|---|---|---|---|
| `birth_date` | date | **是** | 出生日期 `YYYY-MM-DD` |
| `birth_hour` | number (0-23) | 否 | 出生小时，默认 0 |
| `gender` | select | 否 | value：`male` / `female` / `unknown`，默认 `unknown`；代码内映射 `{"male":"男","female":"女","unknown":"unknown"}` |

调用：`bone_weight.calculate(birth_dt, gender_cn)`

#### T7.4 `zhuge_qian` — 诸葛神数

| 参数 | type | 必填 | 说明 |
|---|---|---|---|
| `chars` | string | **是** | 三个汉字，如 `找工作` |

调用：`methods.zhuge.calculate(chars)`

#### T7.5 `xiao_liu_ren` — 小六壬

| 参数 | type | 必填 | 说明 |
|---|---|---|---|
| `date` | date | 否 | 默认今天 |
| `hour` | number (0-23) | 否 | 默认当前小时 |

调用：`xiao_liu_ren.calculate(dt, question)`

#### T7.6 `ling_qian` — 关帝灵签

| 参数 | type | 必填 | 说明 |
|---|---|---|---|
| `qian_number` | number (1-100) | 否 | 不填则随机抽取 |
| `seed` | string | 否 | 可复现种子 |

调用：`ling_qian.calculate(qian_number, question, seed=None)`（见 T8）

#### T7.7 `coin_hexagram` — 金钱卦

| 参数 | type | 必填 | 说明 |
|---|---|---|---|
| `throws` | string | 否 | 六爻结果，逗号分隔，如 `7,8,9,6,7,8`（只能 6/7/8/9）；不填则随机 |
| `seed` | string | 否 | 可复现种子 |

调用：`coin_hexagram.calculate(throws=None, question="", seed=None)`（见 T8）

**判据 C7：**

```bash
cd "G:/code/dify-plugin-cyber-oracle" && python -c "
import yaml, pathlib
tools = ['plum_blossom','tarot','bone_weight','zhuge_qian','xiao_liu_ren','ling_qian','coin_hexagram']
for t in tools:
    d = yaml.safe_load(open(f'tools/{t}.yaml', encoding='utf-8'))
    assert d['identity']['name'] == t, (t, d['identity']['name'])
    names = {p['name'] for p in d['parameters']}
    assert {'question','model','interpret'} <= names, (t, names)
    m = [p for p in d['parameters'] if p['name']=='model'][0]
    assert m['type']=='model-selector' and m['scope']=='llm' and m['required'] is False, t
    assert d['output_schema']['type']=='object', t
    assert set(d['output_schema']['properties']) == {'method','summary','result','interpretation'}, t
    assert d['extra']['python']['source'] == f'tools/{t}.py', t
    assert set(d['identity']['label']) >= {'en_US','zh_Hans'}, t
    assert pathlib.Path(f'tools/{t}.py').exists(), t
    print('OK', t, sorted(names))
print('C7 OK')
"
```

---

### T8 — 给三个随机方法加 seed（**只加参数，不改逻辑**）

**文件：** `methods/tarot.py`、`methods/ling_qian.py`、`methods/coin_hexagram.py`

**改什么（仅此三处）：**

1. `tarot.py` 的 `calculate(dt, question)` → `calculate(dt, question, seed=None, spread_name="三张牌阵")`
   - `seed` 不为 None 时，用它作为 `shuffle_and_draw` 的 `seed_text`；为 None 时**沿用原逻辑**（用 dt + question 拼 seed_text）。
   - `spread_name` 默认值必须是 `"三张牌阵"`，保持原行为。
2. `ling_qian.py` 的 `calculate(qian_number=None, question="")` → 加 `seed=None`
   - `qian_number` 为 None 时：`rng = random.Random(seed) if seed is not None else random`，用 `rng.randint(1, 100)`。
   - 其余校验逻辑**一字不改**。
3. `coin_hexagram.py` 的 `calculate(throws=None, question="")` → 加 `seed=None`
   - `throws` 为 None 时：`rng = random.Random(seed) if seed is not None else random`，用 `rng.choices((6,7,8,9), weights=(1,3,3,1), k=6)`。
   - **权重 `(1,3,3,1)` 和 `k=6` 不许改**（R6）。

**保留什么：** 函数体其余部分、参数校验、返回 dict 结构（R3）全部不动。

**判据 C8：**

```bash
cd "G:/code/dify-plugin-cyber-oracle" && python -c "
from datetime import datetime
from methods import tarot, ling_qian, coin_hexagram
d = datetime(2026,10,22,15,30)
a = tarot.calculate(d, '测试', seed='abc')
b = tarot.calculate(d, '测试', seed='abc')
assert [c['name'] for c in a['cards']] == [c['name'] for c in b['cards']], 'tarot 不可复现'
assert ling_qian.calculate(seed='x')['qian_number'] == ling_qian.calculate(seed='x')['qian_number']
c1 = coin_hexagram.calculate(seed='y'); c2 = coin_hexagram.calculate(seed='y')
assert c1['original']['name'] == c2['original']['name'], 'coin 不可复现'
assert tarot.calculate(d,'测试')['spread_name'] == '三张牌阵'
print('C8 OK')
"
```

---

### T9 — 图标

**做什么：**

- `_assets/icon.svg` 和 `_assets/icon-dark.svg`：自己画一个简洁的占卜主题图标（八卦/签筒/水晶球任选），**纯 SVG，不含外部资源引用**。
- 不要复制别人有版权的图标。

**判据 C9：**

```bash
cd "G:/code/dify-plugin-cyber-oracle" && python -c "
import pathlib
for f in ['_assets/icon.svg','_assets/icon-dark.svg']:
    t = pathlib.Path(f).read_text(encoding='utf-8')
    assert '<svg' in t, f
    assert 'href=\"http' not in t, f
    print('OK', f, len(t))
print('C9 OK')
"
```

---

### T10 — 测试

**做什么：** 在 `tests/` 下建两个**不依赖 dify_plugin** 的测试脚本（直接 `python tests/xxx.py` 跑，不要求 pytest）。

1. `tests/test_methods.py`：7 种方法各跑一次固定输入，断言关键字段存在且类型正确，并断言**同一输入的确定性方法结果一致**。另加一条：`local_now()` 与 UTC 相差 8 小时，且返回值 `tzinfo is None`。
2. `tests/test_manifests.py`：等价于 C2/C3/C7 的合并版，再额外断言：
   - 所有 yaml 能被 `yaml.safe_load` 解析
   - 所有 `extra.python.source` 指向的文件存在
   - 所有 `tools/*.py` 能 `ast.parse` 通过
   - 全仓代码里不含 `api_key` / `openai` / `deepseek.com`（F6）

**判据 C10：**

```bash
cd "G:/code/dify-plugin-cyber-oracle" && python tests/test_methods.py && python tests/test_manifests.py
```

两个脚本都必须以退出码 0 结束，且各自打印 `ALL PASS`。

---

### T11 — .difyignore / README / PRIVACY

**做什么：**

- `.difyignore` 按 **F13** 写。
- `README.md`（英文）：插件名、7 种方法一句话简介、安装方法、参数说明、一句「For entertainment only」。
- `readme/README_zh_Hans.md`（中文）：同上。
- `PRIVACY.md`：说明「插件不上传任何数据到第三方；排盘在本地完成；使用解读功能时数据经 Dify 工作区所选模型处理」。

**判据 C11：**

```bash
cd "G:/code/dify-plugin-cyber-oracle" && python -c "
import pathlib
ig = pathlib.Path('.difyignore').read_text(encoding='utf-8')
for k in ['.git/','.env','__pycache__/','*.pyc','.venv/','*.difypkg','tests/']:
    assert k in ig, k
for f in ['README.md','readme/README_zh_Hans.md','PRIVACY.md']:
    assert pathlib.Path(f).stat().st_size > 100, f
assert 'entertainment' in pathlib.Path('README.md').read_text(encoding='utf-8').lower()
print('C11 OK')
"
```

---

### T12 — 安装依赖 + 跑通本地导入

**做什么：**

```bash
cd "G:/code/dify-plugin-cyber-oracle"
python -m venv .venv
.venv/Scripts/python -m pip install -U pip
.venv/Scripts/python -m pip install -r requirements.txt
```

> 本机是 Python 3.13；若 `dify_plugin` 装不上，改用 `py -3.12 -m venv .venv` 重建（插件运行时声明的是 3.12）。**不要 `pip install` 到全局环境。**

**判据 C12：**

```bash
cd "G:/code/dify-plugin-cyber-oracle" && .venv/Scripts/python -c "
import dify_plugin
from dify_plugin import Tool, ToolProvider, Plugin, DifyPluginEnv
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.entities.model.message import SystemPromptMessage, UserPromptMessage
print('dify_plugin OK', dify_plugin.__version__ if hasattr(dify_plugin,'__version__') else '')
import main
print('C12 OK')
"
```

---

### T13 — 打包

**做什么：**

有 `dify` CLI 就用官方命令；没有就手动打 zip（`.difypkg` 本质是 zip，但**优先官方命令**）：

```bash
# 优先
dify plugin package ./dify-plugin-cyber-oracle -o ./dist

# 兜底（无 CLI 时）
cd G:/code && python -c "
import zipfile, pathlib
root = pathlib.Path('dify-plugin-cyber-oracle')
out = pathlib.Path('dify-plugin-cyber-oracle/cyber-oracle-0.0.1.difypkg')
skip = {'.git','.venv','__pycache__','tests','dist'}
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in root.rglob('*'):
        if p.is_dir() or any(s in p.parts for s in skip): continue
        if p.name.endswith('.pyc') or p.name.endswith('.difypkg'): continue
        if p.name in ('ZCode-任务书-0.0.1.md','DIFY-PLUGIN-SPEC.md','.env'): continue
        z.write(p, p.relative_to(root).as_posix())
print('written', out, out.stat().st_size)
"
```

**判据 C13：**

```bash
cd "G:/code/dify-plugin-cyber-oracle" && python -c "
import zipfile
z = zipfile.ZipFile('cyber-oracle-0.0.1.difypkg')
names = z.namelist()
assert 'manifest.yaml' in names
assert 'main.py' in names
assert sum(1 for n in names if n.startswith('tools/') and n.endswith('.yaml')) == 7
assert sum(1 for n in names if n.startswith('data/') and n.endswith('.json')) == 5
assert not any('.git/' in n or '__pycache__' in n or n.endswith('.pyc') for n in names)
assert not any(n.startswith('tests/') for n in names)
assert not any('ZCode-' in n or 'DIFY-PLUGIN-SPEC' in n for n in names)
print('C13 OK', len(names), 'files')
"
```

---

### T14 — 静态回归自查（对照保留清单）

**做什么：** 逐条对照 R1–R8，把结论写进报告。特别检查：

- `git diff --no-index G:/code/赛博神棍/methods G:/code/dify-plugin-cyber-oracle/methods` 只看差异，**差异只允许**出现在 T8 指定的三个函数签名 + 内部 seed 逻辑、以及 print 删除。
- data 文件 MD5 与源一致（C1 已验）。
- **F17 时间源检查**：`tools/` 下不许出现裸 `datetime.now()`；`methods/` 一行不改（R8）。

**判据 C14：**

```bash
cd "G:/code/dify-plugin-cyber-oracle" && python -c "
import pathlib, re
bad = []
for p in pathlib.Path('tools').rglob('*.py'):
    t = p.read_text(encoding='utf-8')
    for pat in [r'datetime\.now\(', r'datetime\.utcnow\(', r'datetime\.today\(']:
        if re.search(pat, t):
            bad.append((str(p), pat))
assert not bad, bad
print('F17 OK: tools/ 无裸 now()')
"
```

报告里给出上面 diff 的实际输出（不允许写"应该没问题"）。

---

### T15 — 交付报告

**做什么：** 写 `ZCode-报告-0.0.1.md`，必须包含：

1. F1–F16 逐条「✅/❌ + 证据（命令原文 + 输出摘要）」。
2. R1–R7 逐条「✅/❌ + 怎么验的」。
3. C1–C13 每条判据的**实际输出**（不许只写"通过"）。
4. T14 的 diff 输出。
5. 已知问题/未完成项（如实写，不许美化）。

**然后停下，报告给主人。真机安装（T16）由主人或克劳德酱完成**（需要 Dify 登录态，ZCode 没有）。

---

### T16 — 真机验收（**不由 ZCode 执行**，写在这里备查）

1. 打开 `http://localhost`（WSL `ubuntu-dify` 里的 Dify 1.17.1）
2. 右上角 插件 → 安装插件 → 本地文件 → 选 `cyber-oracle-0.0.1.difypkg`
3. 装好后确认能看到 provider「赛博神棍」和 7 个 tool
4. 新建 Workflow：开始 → 工具节点（选 `tarot`）→ 结束
5. 节点参数：`question` 填「我该不该换工作」，`model` 选工作区已配模型，`interpret` 开
6. 运行，确认输出里同时有：排盘摘要、结构化 JSON、AI 解读
7. 再用 `interpret=false` 跑一次，确认不调模型也能出排盘

---

## 4. 附：Dify 插件规范要点（详细版见 `DIFY-PLUGIN-SPEC.md`）

- **目录规则**：图片进 `_assets/`，代码文件在 yaml 里写相对插件根的路径。
- **manifest 必填**：`version` `type` `author` `name` `label` `description` `icon` `resource` `plugins` `meta`。
- **权限**：调模型必须 `resource.permission.model.enabled=true` + `llm=true`。
- **Tool 实现**：继承 `dify_plugin.Tool`，实现 `_invoke(self, tool_parameters) -> Generator[ToolInvokeMessage]`。
- **返回**：`create_text_message` / `create_json_message` / `create_variable_message` 等。
- **output_schema 陷阱**：声明了变量名，就必须真的 `create_variable_message` 返回，否则 workflow 拿到 `None`。
- **反向调用**：`self.session.model.llm.invoke(model_config=..., prompt_messages=[...], stream=False)`。
- **打包**：`dify plugin package ./<dir>` → `.difypkg`。

---

## 5. 最后提醒

- 遇到判据失败：**停下、贴出失败输出、说明卡在哪**。不要自己换方案糊过去。
- 不确定某个 yaml 字段：查 `DIFY-PLUGIN-SPEC.md`，还查不到就停下来问，**不要猜**。
- 每完成一个 T，立刻跑该 T 的判据；不要攒到最后一起跑。
