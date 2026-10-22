# 交付报告：赛博神棍 Dify 插件 v0.0.1

> 执行：ZCode（GLM），2026-10-22
> 施工目录：`G:\code\dify-plugin-cyber-oracle\`（按任务书写死）
> 素材源：`G:\code\赛博神棍\`（全程只读，见 R4）

---

## 0. 结论一句话

**T1–T15 全部完成，C1–C13 判据全绿，R1–R7 逐条核过。** 产出
`cyber-oracle-0.0.1.difypkg`（368,604 字节，45 文件）已就位，待真机安装（T16）。
过程中遇到两处任务书与现实不符（zhdate 版本号、dify_plugin 类加载器行为），
均已按「最小改动」处理并如实记录在 §5。

---

## 1. F1–F16 逐条对照

| 编号 | 结论 | 证据 |
|---|---|---|
| F1 目录结构 | ✅ | 见 C13 包内清单：`manifest.yaml` `main.py` `requirements.txt` `.difyignore` `_assets/` `provider/` `tools/` `methods/` `utils/` `data/` 齐备 |
| F2 manifest 字段 | ✅ | C2 OK（type/name/author/version 双写/memory=268435456/model.enabled+llm/runner 3.12+main/label 双语） |
| F3 model 权限 | ✅ | C2 断言 `resource.permission.model.enabled is True` 且 `llm is True`；C12 运行时打印的 manifest JSON 里 `"model":{"enabled":true,"llm":true,...}` 实证 |
| F4 7 个 tool | ✅ | C7 七个 yaml+py 全过；provider yaml `tools:` 列 7 条（C3） |
| F5 公共参数 | ✅ | C7 断言 `{'question','model','interpret'} <= names`，model 是 `model-selector`+`scope: llm`+`required: false`；interpret 是 boolean+default true；`_maybe_interpret` 里 model 为空/interpret=False 时直接跳过解读（`tools/base.py`） |
| F6 只走反向调用 | ✅ | `utils/interpret.py` 只含 `session.model.llm.invoke`；全仓 `api_key`/`OpenAI(`/`api.deepseek.com`/`local-broker` 零命中（C5 + tests/test_manifests.py `check_no_forbidden_tokens`） |
| F7 解读失败不阻断 | ✅ | `tools/base.py` `_maybe_interpret` 用 try/except 包解读，异常返回 `( "", "[解读失败] {type}: {e}" )`，note 拼进 summary，排盘照常输出 |
| F8 四变量输出 | ✅ | `_emit` 依次 yield `method`/`summary`/`result`/`interpretation` 四个 `create_variable_message` + `create_json_message` + `create_text_message` |
| F9 output_schema | ✅ | C7 断言每 tool `output_schema.properties == {'method','summary','result','interpretation'}` |
| F10 数据 5 JSON | ✅ | C1 MD5 与源一致；`data_loader.py` 显式 `encoding="utf-8"`（源码自带，未改） |
| F11 seed 可复现 | ✅ | C8：tarot 同 seed 同牌序；ling_qian 同 seed 同签号；coin 同 seed 同 throws；不传 seed 行为不变（test_methods.py 里另有 30/50 次随机抽样断言） |
| F12 i18n 双语 | ✅ | C7 断言每 tool label 含 en_US+zh_Hans；test_manifests.py `check_i18n` 加码断言了每个参数的 label 也双语 |
| F13 .difyignore | ✅ | C11：`.git/`、`.env`、`__pycache__/`、`*.pyc`、`.venv/`、`*.difypkg`、`tests/`、`ZCode-*.md`、`DIFY-PLUGIN-SPEC.md` 全挡（另加 `dist/`） |
| F14 文档齐备 | ✅ | C11：README.md（含 For entertainment only）/ readme/README_zh_Hans.md / PRIVACY.md 均 >100 字节 |
| F15 自包含 | ✅ | C4 全仓 .py 无 `赛博神棍`/`G:` 字样、无 sys.path 魔法（tests/test_methods.py 用 `parents[1]` 加根属测试脚本自定位，且该目录被打包排除，不算插件代码） |
| F16 打包干净 | ✅ | C13：45 文件，无 .git/__pycache__/pyc/tests/任务书；7 tool yaml + 5 data json 齐全 |

## 2. R1–R7 逐条对照

| 编号 | 结论 | 怎么验的 |
|---|---|---|
| R1 算法口径一致 | ✅ | T14 diff：methods/ 下仅 3 个文件有代码 diff，全部是 T8/T4 指定改动（见 §4）；plum_blossom/bone_weight/xiao_liu_ren/zhuge（除 print）零改动；utils/ 三文件零 diff。「找工作」→69 锚点在 test_methods.py 通过 |
| R2 数据原样 | ✅ | C1 五份 JSON MD5 与源逐一相等 |
| R3 字段名沿用 | ✅ | 七个 `calculate()` 返回 dict 的构造代码零改动（diff 佐证）；tool 层只加 `result["method"] = METHOD_NAME` 的覆盖逻辑（各方法的 method 值本就等于 METHOD_NAME，覆盖是幂等的）与 datetime→ISO 序列化，不重命名任何字段 |
| R4 源项目零改动 | ✅ | `find G:/code/赛博神棍 -newermt 2026-10-22` 零输出（今天没有任何文件被写）；源项目 `tests/selftest.py` 复跑 ALL PASS |
| R5 提示词沿用 | ✅ | `utils/interpret.py` 的 system/user prompt 文案逐字取自 `llm_module.py` 的 `_interpret_*` 七函数（含塔罗的「注意：第一部分…」长句、三段式结构、「赛博神棍的话，看看就行了」收尾、诸葛的四段式与「别太当真」），只把 `client.chat.completions.create` 换成反向调用 |
| R6 权重不动 | ✅ | diff 实证 `weights=(1, 3, 3, 1), k=6` 只是被包进 rng 变量、字面量未变；tarot.py 除 T8 外零 diff；ling_qian `randint(1, 100)` 未变 |
| R7 无新增依赖 | ✅ | requirements.txt 仅 `dify_plugin>=0.9.0,<0.11.0` + `zhdate>=0.1`（版本约束修正见 §5，包本身是 R7 允许的两个） |

## 3. C1–C13 判据实际输出

```
C1 OK（前五行）
OK iching_full.json 63191
OK kangxi_strokes.json 183790
OK ling_qian_guan_di.json 55270
OK xiaoliuren.json 3397
OK zhuge_qian.json 514764
C1 OK

C2 OK

C3 OK ['tools/plum_blossom.yaml', 'tools/tarot.yaml', 'tools/bone_weight.yaml',
       'tools/zhuge_qian.yaml', 'tools/xiao_liu_ren.yaml', 'tools/ling_qian.yaml',
       'tools/coin_hexagram.yaml']

C4: data dir: G:\code\dify-plugin-cyber-oracle\data
    C4 OK

C5 OK
C6 OK

C7（七行，节选）
OK plum_blossom ['date', 'hour', 'interpret', 'model', 'question']
OK tarot ['interpret', 'model', 'question', 'seed', 'spread']
OK bone_weight ['birth_date', 'birth_hour', 'gender', 'interpret', 'model', 'question']
OK zhuge_qian ['chars', 'interpret', 'model', 'question']
OK xiao_liu_ren ['date', 'hour', 'interpret', 'model', 'question']
OK ling_qian ['interpret', 'model', 'qian_number', 'question', 'seed']
OK coin_hexagram ['interpret', 'model', 'question', 'seed', 'throws']
C7 OK

C8 OK

C9 OK（icon.svg / icon-dark.svg 各 1040 字节）

C10:
OK test_plum_blossom … OK test_coin_hexagram（7 行 OK）
ALL PASS
=====
OK manifest / OK provider / OK tools / OK i18n / OK no forbidden tokens
ALL PASS

C11 OK

C12:
dify_plugin OK
{"version":"0.0.1","type":"plugin",...,"resource":{"memory":268435456,
"permission":{"model":{"enabled":true,"llm":true,...}}},...}
{"event": "log", "data": {"level": "INFO", "message": "Installed tool: cyber_oracle", ...}}
C12 OK

C13 OK 45 files（文件清单见 §6）
```

## 4. T14 diff 实际输出（methods 侧，剔除 pycache 噪音）

`git diff --no-index 赛博神棍/methods dify-plugin-cyber-oracle/methods` 的代码差异**全集**：

```diff
--- coin_hexagram.py
-def calculate(throws: list | None = None, question: str = "") -> dict:
+def calculate(throws: list | None = None, question: str = "", seed=None) -> dict:
     if throws is None:
-        normalized = random.choices((6, 7, 8, 9), weights=(1, 3, 3, 1), k=6)
+        rng = random.Random(seed) if seed is not None else random
+        normalized = rng.choices((6, 7, 8, 9), weights=(1, 3, 3, 1), k=6)

--- ling_qian.py
-def calculate(qian_number: int | None = None, question: str = "") -> dict:
+def calculate(qian_number: int | None = None, question: str = "", seed=None) -> dict:
     if qian_number is None:
-        qian_number = random.randint(1, 100)
+        rng = random.Random(seed) if seed is not None else random
+        qian_number = rng.randint(1, 100)

--- tarot.py
-def calculate(dt: datetime, question: str) -> dict:
+def calculate(dt: datetime, question: str, seed=None, spread_name="三张牌阵") -> dict:
     （docstring 增加 seed/spread_name 两行说明）
-    # 默认使用三张牌阵
-    spread_name = "三张牌阵"
-    seed = f"{question}||{dt.isoformat()}"
-    drawn, spread = shuffle_and_draw(spread_name, seed)
+    if seed is not None:
+        seed_text = str(seed)
+    else:
+        seed_text = f"{question}||{dt.isoformat()}"
+    drawn, spread = shuffle_and_draw(spread_name, seed_text)

--- zhuge.py
     except FileNotFoundError:
-        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
-                                 "data", "zhuge_qian.json")
-        print(f"[警告] 找不到诸葛神数签文数据：{data_path}")
+        （直接返回空 dict，兜底签逻辑保留）
```

其余文件（plum_blossom / bone_weight / xiao_liu_ren / 其余 utils）零代码 diff。
diff 输出里的其余条目全是：__pycache__ 二进制噪音、以及源目录 `methods/utils/`
重复副本（任务书 T1 第 3 条明确不复制）在 diff 里显示为 deleted。

## 5. 已知问题 / 偏差（如实记录）

1. **`zhdate>=0.1.6` 装不上，改为 `zhdate>=0.1`**：PyPI 上 zhdate 只发布过
   `0.1` 一个版本（`pip index versions zhdate` 实测只有 0.1），任务书的
   `>=0.1.6` 是无解约束。全局环境与源 CLI 项目用的也是 0.1。`lunar.py`
   在 0.1 下工作正常（源项目 selftest + 本插件 test_methods 双重验证）。
   **此改动属于任务书与 PyPI 现实的冲突修正，不是降级**——可满足该约束的
   版本本来就不存在。
2. **tool 源文件 import 写法受 dify_plugin 类加载器约束**：`dify_plugin
   0.10.2` 的 `load_single_subclass_from_source` 会把模块命名空间里**所有**
   `Tool` 子类都数进去，`from tools.base import BaseOracleTool` 导致
   "Multiple subclasses of Tool" 报错。已改为 `from tools import base` +
   `base.BaseOracleTool`（首装 C12 失败、修后通过的完整过程见 C12）。
   这是 dify_plugin 的实际行为，不是代码缺陷；任务书 T6 的示例写法在
   0.10.2 下装不上，属任务书编写时未预见的运行时约束。
3. **打包走的是任务书兜底 zip 方案**：本机无 `dify` CLI（`which dify` 为空）。
   `.difypkg` 本质是 zip，排除规则与任务书兜底脚本一致。
4. **`methods/zhuge.py` 保留 `import os`**：删 print 后 `os` 不再被使用，
   但按「最小 diff」原则未清理（不影响功能与打包）。
5. **未验项（超出本任务范围，留给 T16 真机验收）**：
   - 反向调用 `session.model.llm.invoke` 在 Dify 1.17.1 真机的实际行为
     （本地无 Dify 登录态，无法端到端验证）；
   - `model-selector` 参数在 workflow 节点 UI 的实际呈现；
   - `date` 类型参数传入的精确格式（代码按 `YYYY-MM-DD` 解析，兼容性待真机确认）。

## 6. 包内文件清单（C13 顺带输出）

```
.difyignore  PRIVACY.md  README.md  manifest.yaml  main.py  requirements.txt
_assets/icon.svg  _assets/icon-dark.svg
data/{SOURCES.md, iching_full.json, kangxi_strokes.json, ling_qian_guan_di.json, xiaoliuren.json, zhuge_qian.json}
methods/{__init__, bone_weight, coin_hexagram, ling_qian, plum_blossom, tarot, xiao_liu_ren, zhuge}.py
provider/{cyber_oracle.yaml, cyber_oracle.py}
readme/README_zh_Hans.md
tools/{base.py, 7×(name.yaml + name.py)}
utils/{__init__, data_loader, hexagram, lunar, interpret}.py
```

## 7. T16 待办（主人或克劳德酱执行）

1. `http://localhost` → 插件 → 安装插件 → 本地文件 →
   选 `G:\code\dify-plugin-cyber-oracle\cyber-oracle-0.0.1.difypkg`
2. 确认 provider「赛博神棍」+ 7 个 tool 可见
3. Workflow：开始 → tarot 工具节点（question=「我该不该换工作」，选模型，
   interpret 开）→ 结束；确认排盘摘要 / JSON / AI 解读三者齐
4. `interpret=false` 再跑一次：不调模型、只出排盘
