# Cyber Oracle

Seven Chinese divination methods as a Dify tool plugin. Casting is fully
deterministic local computation — **it works with no model configured at all**.
AI interpretation is an optional enhancement that reverse-invokes the LLM already
set up in your Dify workspace; the plugin never stores an API key.

> **For entertainment only.** Divination results are not factual predictions and
> should not be used to make decisions.

**Chinese documentation:** [readme/README_zh_Hans.md](readme/README_zh_Hans.md)

---

## Why Install It

- **Zero-dependency casting** — no model, no network, still works. Usable as a
  pure computation node inside a Workflow.
- **Optional interpretation** — set `interpret=false` or leave the model empty
  and the plugin makes **zero model calls**.
- **Reproducible** — Tarot, Guan Di lots and Coin Hexagram accept a `seed`; the
  same seed always yields the same draw.
- **Timezone-aware** — a container running in UTC will not silently compute a
  different hexagram (see [Timezone](#timezone)).
- **No stored credentials** — the plugin holds no API key; interpretation uses
  the model configured in your own workspace.

---

## The Seven Methods

| Tool | Method | What it does |
|---|---|---|
| `plum_blossom` | Plum Blossom | Time-based hexagram from date and hour: original hexagram, changed hexagram, moving line |
| `tarot` | Tarot | Draw 1 / 3 / 10 cards (single card, three-card spread, Celtic Cross), upright or reversed |
| `bone_weight` | Bone Weight | Yuan Tiangang bone-weight fortune from birth date and hour |
| `zhuge_qian` | Zhuge Oracle | Report three Chinese characters, receive one of 384 oracle poems |
| `xiao_liu_ren` | Xiao Liu Ren | Palm-counting divination from month, day and hour |
| `ling_qian` | Guan Di Lots | Draw one of 100 Guan Di oracle lots (random or by number) |
| `coin_hexagram` | Coin Hexagram | I Ching hexagram from six coin tosses (6/7/8/9), supporting static and multi-moving-line readings |

---

## Installation

1. In Dify, open **Plugins → Install Plugin → Local File**
2. Select `cyber-oracle-0.0.1.difypkg`
3. After installation you get the provider **Cyber Oracle** with seven
   tools

Then add a **tool node** in a Workflow, choose a method, fill in the parameters,
and pick a model if you want interpretation.

### Build from source

```bash
pip install dify-plugin>=0.9.0
python -m main
```

To package:

```bash
dify plugin package ./dify-plugin-cyber-oracle
```

---

## What It Looks Like

Drop in a tool node, pick the `tarot` tool:

| Parameter | Value |
|---|---|
| `question` | Should I take this offer? |
| `spread` | `three_card` |
| `model` | any LLM in your workspace (omit to cast only) |

The tool returns three things:

- **A text message** — human-readable casting summary plus AI interpretation
- **JSON** — the full structured result, for passing data between nodes
- **Four output variables** — `method` / `summary` / `result` / `interpretation`,
  referenceable directly in the workflow

---

## Parameters

Three parameters are shared by all seven tools:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `question` | string | empty | The matter you are asking about; fed to interpretation |
| `model` | model selector | — | LLM for interpretation; leave empty to cast only |
| `interpret` | boolean | `true` | Whether to generate an AI interpretation |

Method-specific parameters:

| Tool | Specific parameters |
|---|---|
| `plum_blossom` / `xiao_liu_ren` | `date` (YYYY-MM-DD, defaults to today), `hour` (0-23, defaults to the current hour) |
| `tarot` | `spread` (`single_card` / `three_card` / `celtic_cross`), `seed` |
| `bone_weight` | `birth_date` (required), `birth_hour`, `gender` (`male` / `female` / `unknown`) |
| `zhuge_qian` | `chars` (three Chinese characters, required) |
| `ling_qian` | `qian_number` (1-100, random when omitted), `seed` |
| `coin_hexagram` | `throws` (six comma-separated values, each 6/7/8/9; random when omitted), `seed` |

### Outputs

Every tool returns four variables, declared in `output_schema` so workflows can
reference them:

- `method` — method name (string)
- `summary` — human-readable casting summary (string)
- `result` — full structured casting result (object)
- `interpretation` — AI interpretation (string; empty when skipped or failed)

Plus a full JSON message and a human-readable text message. If interpretation
fails, the casting result is still returned and the failure reason is noted in
`summary`.

---

## Timezone

Time-based methods (Plum Blossom, Xiao Liu Ren) are sensitive to timezone —
**eight hours of offset is a different hexagram**. The plugin resolves the
timezone in this order:

1. The `timezone` tool parameter, when the tool exposes one
2. The **Timezone** field in the provider credentials (set once at install, shared
   by all seven tools)
3. The plugin container's `TZ` environment variable
4. Fallback to `Asia/Shanghai`

For a self-hosted Dify, setting `TZ` on the plugin container is the simplest
option. For cloud deployments, fill in your local timezone in the provider
credentials.

When only `date` is given without `hour`, the current hour is used; pass `hour`
explicitly for historical lookups.

---

## Privacy

Casting runs entirely locally — no network, no upload. When AI interpretation is
enabled, the hexagram and your question are sent to **the model you configured in
your own workspace**; that model provider is the only recipient. See
[`PRIVACY.md`](PRIVACY.md) for details.

---

## Data and Credits

The algorithms and oracle texts come from the
[Cyber Oracle CLI project](https://github.com/Kagurazaka135/code-sanctuary). Data
provenance and licensing are documented in [`data/SOURCES.md`](data/SOURCES.md).

The modern-language readings for the Zhuge Oracle are generated by the scripts in
[`scripts/`](scripts/README.md) from public-domain source poems and classical
commentary; no third-party compiled text is used.

**Network access:** none. The plugin makes no outbound requests; interpretation
travels through Dify's own reverse invocation channel.

---

## Disclaimer

For entertainment only. Divination output is generated by probabilistic models and
must not be treated as factual prediction, professional advice, or a basis for
decisions with financial or personal consequence.
