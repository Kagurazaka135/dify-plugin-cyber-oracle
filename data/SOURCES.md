# 数据来源与校验

| 文件 | 内容 | 条数 | 来源 | 许可 |
|---|---|---|---|---|
| `zhuge_qian.json` | 诸葛神数 384 签（签诗/吉凶/断语/文言解 + 本项目生成的现代解读） | 384 | 签诗与文言注解为古代文献（公有领域）；现代解读由本项目用大模型生成，见 [`scripts/`](../scripts/README.md) | **公开领域 + 本项目 MIT** |
| `ling_qian_guan_di.json` | 关帝灵签 100 签（清刊本校勘版） | 100 | [lakeofsky347/dsh-wen_xiang](https://github.com/lakeofsky347/dsh-wen_xiang) `content/lot/guandi-100` | MIT（解读文本），签诗源自维基文库公有领域 |
| `iching_full.json` | 周易 64 卦 + 卦辞 + 爻辞 | 64 卦 / 386 条爻辞 | [john-walks-slow/open-iching](https://github.com/john-walks-slow/open-iching) | 见上游仓库 |
| `kangxi_strokes.json` | 康熙笔画字典（字 → 笔画数） | 20794 字 | [shunshi-kangxi-core](https://www.npmjs.com/package/shunshi-kangxi-core) 0.1.1，取 `chars.json` 的 `kx` 字段 | MIT |
| `xiaoliuren.json` | 小六壬六掌诀（口诀 + 六类事项断辞） | 6 | 本项目整理 | 本项目自有 |

## 关于诸葛神数的解读文本

早期的 `zhuge_qian.json` 使用过一份来源不明的二手白话解读，许可不明。现已全部
弃用，改为**从公有领域的签诗与文言解重新生成**：

- 输入只有 `poem` / `verdict` / `commentary` / `title`，全部是古代文献
- 生成脚本与产出说明见 [`scripts/`](../scripts/README.md)
- 输入中从未读取过任何第三方解读文本，产出物不存在衍生关系

## 校验结果

- 诸葛神数：`number` 1–384 连续无重复，各字段非空，解读长度 67–303 字（平均 209）。
- 关帝灵签：`number` 1–100 连续无重复，签诗与解读无缺失。
- 周易：64 卦 id 1–64 连续，每卦 6 条爻辞（乾坤另含用九/用六，合计 386 条），卦辞无缺失。
- 康熙笔画：20794 字，`kx` 全为整数；已验证「找=8、工=3、作=7」，与 spec 示例一致。

## 已知数据瑕疵

- 第 123、300、90 签的 `fortune`（签等）与 `verdict` / `commentary` 正文语气不一致
  （如第 300 签标「中下签」，正文却写「大吉大利」）。这属于原始流传版本的内部矛盾，
  本版本未擅自改动，AI 解读会综合两边给判断。
- 第 189 签原标「上上签」，但签诗（「渴望梅，饥画饼，漫劳心，如捉影」）与断语均指向凶，
  已按内容修正为「中下签」。

## 注意

- 关帝灵签签诗保留**繁体**（清刊本校勘版原样），不要自动转简体。
- 康熙笔画是**康熙字典标准**，不是简体笔画；同一字简繁可能不同（如「爱」10 画 / 康熙 13 画）。
- 诸葛神数的 `interpretation` 是模型生成的白话，属诠释而非考据，仅供娱乐。
