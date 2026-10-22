# 诸葛神数解读生成脚本

## 这个目录是干什么的

本插件 `data/zhuge_qian.json` 里那 384 条**现代白话解读**，是用本目录的脚本
生成出来的。这份文档说明：原始素材从哪来、哪些内容有版权、我们怎么绕开的。

## 免责声明

### 关于签文

诸葛神数 384 签的**签诗、文言注解、卦名、宫位**均为古代文献，属于公有领域
（public domain），任何人都可以使用。

### 关于解读

坊间流传的各种「诸葛神数白话解」版本，来源多为无明确授权的二手整理，
**不能确认为自由许可内容**。本插件因此**不使用任何第三方整理的白话解读**。

`data/zhuge_qian.json` 中的 `interpretation` 字段，全部由本项目用大语言模型
**从公有领域的签诗与文言解重新生成**，不包含任何第三方解读原文。

### 产出物的许可

本脚本及其生成的解读文本，随本项目以 **MIT** 分发。

### 局限

模型生成的解读可能存在与古籍原意有出入之处。本项目认为这是可接受的：
这类解读本质上属于诠释而非考据，但它**不能替代专业命理咨询，也仅供娱乐**。

## 怎么跑

### 前置条件

脚本调用**本地凭证代理**，不在代码里存任何 API Key：

```bash
# 代理默认监听 127.0.0.1:9999
curl http://127.0.0.1:9999/healthz
```

如果你的环境没有这套代理，可以设置环境变量指向任意 OpenAI 兼容端点：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `BROKER_URL` | `http://127.0.0.1:9999` | 兼容 `/v1/chat/completions` 的端点 |
| `BROKER_KEY` | `local-broker` | API Key（走代理时填假值即可） |
| `GEN_MODEL` | `deepseek-flash` | 生成用的模型 |
| `GEN_WORKERS` | `8` | 并发数 |

### 运行

```bash
# 先抽几条看效果
python gen_zhuge_interpretations.py --limit 5

# 全量生成（384 条，8 并发约 3-5 分钟）
python gen_zhuge_interpretations.py

# 中途失败可以续跑，已生成的不会重算
python gen_zhuge_interpretations.py --resume
```

### 产出

写入 `data/zhuge_qian_generated.json`，结构如下：

| 字段 | 来源 | 说明 |
|---|---|---|
| `number` / `title` / `palace` / `fortune` / `poem` / `verdict` / `commentary` | 古籍，公有领域 | 原样保留 |
| `interpretation` | **本脚本生成** | 现代白话解读 |
| `_fortune_review` | 本脚本生成 | 模型对吉凶的独立判断，**仅供人工核对，不进最终数据** |

`_fortune_review` 是给校对用的：如果它和原始 `fortune` 差得离谱，说明那条数据
可能有问题（实测确实抓到几条错标）。

## 模型与参数

- 模型：`deepseek-flash`（可通过 `GEN_MODEL` 换）
- 温度：`0.8`
- 解读长度：120～220 字
- 复核单独调用一次，只要求输出吉凶词

## 校验

跑完之后建议做一次抽查：

```bash
python -c "
import json
d = json.load(open('../data/zhuge_qian_generated.json', encoding='utf-8'))
print('条数:', len(d))
print('空解读:', sum(1 for v in d.values() if not v.get('interpretation')))
print('平均字数:', sum(len(v['interpretation']) for v in d.values()) // len(d))
"
```

预期：条数 384、空解读 0、平均字数 150-200。
