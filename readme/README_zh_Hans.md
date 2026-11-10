# 赛博神棍 · Cyber Oracle

[English](../README.md)

装进 Dify 的九种算命工具——七种经典方法，外加自动选法和一卦三问。排盘全是本地确定性计算，**一个模型都不配也能用**。

> **仅供娱乐。** 排盘结果不构成事实预测，也不该拿来决策。

## 特点

- **不需要任何凭据**：排盘纯本地，插件不存 API Key，也不发起任何外部网络请求。
- **不配模型也能用**：每个工具都返回完整结构化结果；AI 解读是可选项，走 Dify 反向调用，用的是你工作区里已配置的模型。
- **可复现**：塔罗、关帝灵签、金钱卦支持 `seed`，同一个 seed 永远同一卦。
- **时区可配**：容器跑 UTC 也不会把按时间起卦的方法算错。
- **可串联**：每个工具都输出 `method` / `summary` / `result` / `interpretation` 四个变量，供下游节点引用。

## 工具

| 工具 | 干什么 |
|---|---|
| `plum_blossom` | 按日期时辰起梅花易数时间卦，出本卦、变卦、动爻 |
| `tarot` | 抽 1 / 3 / 10 张塔罗，含正逆位 |
| `bone_weight` | 按出生日期时辰查袁天罡称骨歌 |
| `zhuge_qian` | 报三个汉字，得诸葛神数 384 签之一 |
| `xiao_liu_ren` | 按月、日、时推小六壬六掌诀 |
| `ling_qian` | 抽关帝灵签 100 签之一 |
| `coin_hexagram` | 六次掷币（6/7/8/9）起金钱卦 |
| `auto_route` | 只看问题，自动挑最合适的方法再起卦 |
| `multi_cast` | 同时用多种方法起卦，并汇总成一份判断 |

## 安装

1. 在 Dify 里打开 **插件 → 安装插件 → 本地文件**，选 `cyber-oracle-<版本>.difypkg`。
2. 无需 API Key 或任何连接。可在 provider 凭据里填 **时区**（默认 `Asia/Shanghai`），让按时间起卦的方法贴合本地时间。

从源码构建需要 `dify-plugin>=0.9.0`，打包命令 `dify plugin package ./dify-plugin-cyber-oracle`。

## 用法

在 Workflow 里拖一个**工具节点**，选一个工具：

| 参数 | 示例 |
|---|---|
| `question` | 这个 offer 要不要接 |
| `interpret` | `true` |
| `model` | 工作区里任意 LLM（不选则只排盘） |

产出三样：

- **文本消息**——人看的排盘摘要；生成了解读就附在后面
- **JSON 消息**——完整结构化结果，节点之间传数据用
- **输出变量**——`method` / `summary` / `result` / `interpretation`

例如 `auto_route` 收到「我钱包丢了怎么办」，会判定为寻物类并选中 `xiao_liu_ren`，直接给出掌诀落位和断辞。`multi_cast` 每路解读各调一次模型、再加一次汇总，比单方法慢也更费额度。

## 隐私

排盘在本地完成，不上传任何内容。开启解读时，卦象结果和你的问题只会发送到**你自己工作区里配置的那个模型**。详见 [`PRIVACY.md`](../PRIVACY.md)。

## 来源与许可

源码仓库：<https://github.com/Kagurazaka135/code-sanctuary>。数据出处与授权见 [`data/SOURCES.md`](../data/SOURCES.md)。
