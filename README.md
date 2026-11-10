# Cyber Oracle

Nine Chinese divination tools for Dify — seven classic methods plus automatic
method selection and multi-method readings. Casting is deterministic local
computation, so **it works with no model configured at all**.

> **For entertainment only.** Results are not factual predictions and should not
> be used as a basis for decisions.

## Features

- **No credentials required** — casting runs entirely offline; the plugin stores
  no API key and makes no outbound network request.
- **Works without a model** — every tool returns a complete structured result.
  AI interpretation is optional and reverse-invokes the LLM already configured
  in your Dify workspace.
- **Reproducible** — Tarot, Guan Di Lots and Coin Hexagram accept a `seed`; the
  same seed always yields the same draw.
- **Timezone-aware** — time-based methods will not silently compute a different
  hexagram on a UTC container.
- **Composable** — every tool exposes `method` / `summary` / `result` /
  `interpretation` variables for downstream nodes.

## Tools

| Tool | What it does |
|---|---|
| `plum_blossom` | Time-based I Ching hexagram: original, changed, moving line |
| `tarot` | Draw 1 / 3 / 10 cards, upright or reversed |
| `bone_weight` | Yuan Tiangang bone-weight fortune from birth date and hour |
| `zhuge_qian` | Report three Chinese characters, receive one of 384 oracle poems |
| `xiao_liu_ren` | Palm-counting divination from month, day and hour |
| `ling_qian` | Draw one of 100 Guan Di oracle lots |
| `coin_hexagram` | I Ching hexagram from six coin tosses (6/7/8/9) |
| `auto_route` | Pick the best-fitting method from the question, then cast it |
| `multi_cast` | Cast several methods at once and merge them into one summary |

## Setup

1. Install the plugin package (`cyber-oracle-<version>.difypkg`) via
   **Plugins → Install Plugin → Local File**.
2. No API key or connection is needed. Optionally set **Timezone** in the
   provider credentials (default `Asia/Shanghai`) so time-based methods match
   your local time.

Building from source requires `dify-plugin>=0.9.0`; package with
`dify plugin package ./dify-plugin-cyber-oracle`.

## Usage

Add a **Tool** node in a Workflow and pick a tool:

| Input | Example |
|---|---|
| `question` | Should I take this offer? |
| `interpret` | `true` |
| `model` | any LLM in your workspace (leave empty to cast only) |

Output:

- **Text message** — readable casting summary, plus the interpretation when one
  was generated
- **JSON message** — full structured result for passing between nodes
- **Variables** — `method`, `summary`, `result`, `interpretation`

For example, `auto_route` given a lost-item question selects `xiao_liu_ren`
(the lost-item topic) and returns the palm position plus its reading.
`multi_cast` costs one model call per method plus one summary call, so it is
slower and uses more quota than a single method.

## Privacy

Casting is local and uploads nothing. When interpretation is enabled, the cast
result and your question are sent only to **the model you configured in your own
workspace**. See [`PRIVACY.md`](PRIVACY.md) for details.

## Source and License

Source repository: <https://github.com/Kagurazaka135/code-sanctuary>. Data
provenance and licensing are documented in [`data/SOURCES.md`](data/SOURCES.md).
