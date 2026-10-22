# -*- coding: utf-8 -*-
"""为诸葛神数 384 签生成现代白话解读。

背景：原始数据里的 `interpretation` 字段来自无明确许可的二手整理，不能随插件
分发。本脚本只用**公有领域**的签诗、断语、文言解作为输入，让模型重新写一份
白话解读——产出物版权归本项目所有，可随插件一起以 MIT 分发。

输入（均为公版内容）：
    poem        签诗原文
    verdict     断语
    commentary  文言解

输出：
    interpretation  新生成的白话解读（本脚本产出）
    fortune_review  模型对吉凶的独立判断，仅供人工核对，不写入数据

用法：
    python gen_zhuge_interpretations.py            # 全量生成
    python gen_zhuge_interpretations.py --limit 5  # 先跑 5 条看效果
    python gen_zhuge_interpretations.py --resume   # 断点续跑

依赖：仅标准库 + 本地凭证代理（见 README.md）。

许可证：本脚本及其产出的解读文本以 MIT 分发。
"""

import argparse
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# ---- 配置 ----
BROKER_URL = os.environ.get("BROKER_URL", "http://127.0.0.1:9999")
BROKER_KEY = os.environ.get("BROKER_KEY", "local-broker")  # 假 key，真钥匙由 broker 注入
MODEL = os.environ.get("GEN_MODEL", "deepseek-flash")
WORKERS = int(os.environ.get("GEN_WORKERS", "8"))
MAX_RETRY = 3

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "zhuge_qian.json"
OUT = ROOT / "data" / "zhuge_qian_generated.json"

SYSTEM_PROMPT = (
    "你是一位解签人。给你一签的签诗、断语和文言解，请写一段现代白话解读。\n"
    "要求：\n"
    "1. 用日常口语，像朋友聊天，不用文言、不用术语堆砌。\n"
    "2. 先说这一签的整体气象，再说到具体事项（事业、财运、感情、健康之类）。\n"
    "3. 如果有需要注意的风险或前提，直说，别一味说好话。\n"
    "4. 不要复述签诗原文，不要逐句翻译。\n"
    "5. 篇幅 120～220 字。\n"
    "6. 不要出现「根据签诗」「此签表示」这类套话，直接说事。\n"
    "7. 只输出解读正文，不要任何前缀、标题或解释。\n"
)

REVIEW_PROMPT = (
    "下面是一签的签诗和注解。请判断这一签的吉凶等级，只输出一个词，"
    "从以下选项里选：上上签、上签、中上签、中签、中下签、下签、下下签。\n"
    "不要输出别的任何内容。"
)

_lock = threading.Lock()
_done = 0


def _post(payload: dict, timeout: int = 90) -> dict:
    req = urllib.request.Request(
        f"{BROKER_URL}/v1/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {BROKER_KEY}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _chat(system: str, user: str, max_tokens: int = 2500) -> str:
    last_err = None
    for attempt in range(MAX_RETRY):
        try:
            data = _post(
                {
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "temperature": 0.8,
                    "max_tokens": max_tokens,
                }
            )
            return (data["choices"][0]["message"]["content"] or "").strip()
        except Exception as exc:  # noqa: BLE001 - 网络层什么都可能抛
            last_err = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"调用失败（重试 {MAX_RETRY} 次）：{last_err}")


def _build_user(entry: dict) -> str:
    parts = [f"第 {entry['number']} 签"]
    if entry.get("title"):
        parts.append(f"卦名：{entry['title']}")
    if entry.get("fortune"):
        parts.append(f"签等：{entry['fortune']}")
    parts.append(f"签诗：{entry['poem']}")
    if entry.get("verdict"):
        parts.append(f"断语：{entry['verdict']}")
    if entry.get("commentary"):
        parts.append(f"文言解：{entry['commentary']}")
    return "\n".join(parts)


def _clean(text: str) -> str:
    text = re.sub(r"^[\s\"'「『]+|[\s\"'」』]+$", "", text)
    text = re.sub(r"^(解读[:：]\s*|第\s*\d+\s*签[:：]\s*)", "", text)
    return text.strip()


MIN_LEN = 60


def _work(number: str, entry: dict) -> tuple[str, str, str]:
    interpretation = ""
    # 推理模型的思考链会先吃 token 额度，偶尔会把 content 挤成空串，重试即可
    for _ in range(MAX_RETRY):
        interpretation = _clean(_chat(SYSTEM_PROMPT, _build_user(entry)))
        if len(interpretation) >= MIN_LEN:
            break
        time.sleep(1.0)
    if len(interpretation) < MIN_LEN:
        raise RuntimeError(f"生成长度不足（{len(interpretation)} 字）")
    review = ""
    try:
        # max_tokens 不能给小：推理模型的思考链会先吃光额度，导致 content 为空
        raw = _chat(REVIEW_PROMPT, _build_user(entry), max_tokens=400)
        review = re.search(r"(上上签|上签|中上签|中签|中下签|下签|下下签)", raw)
        review = review.group(1) if review else ""
    except Exception:  # noqa: BLE001 - 复核失败不影响主产物
        pass
    return number, interpretation, review


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="只跑前 N 条，用于抽查")
    ap.add_argument("--resume", action="store_true", help="跳过已生成且长度合格的条目")
    args = ap.parse_args()

    source = json.loads(SRC.read_text(encoding="utf-8"))
    numbers = sorted(source, key=lambda x: int(x))
    if args.limit:
        numbers = numbers[: args.limit]

    results: dict[str, dict] = {}
    if args.resume and OUT.exists():
        results = json.loads(OUT.read_text(encoding="utf-8"))
        print(f"续跑：已有 {len(results)} 条")

    if args.resume:
        # 已生成但长度不足的也要重跑
        todo = [
            n
            for n in numbers
            if n not in results
            or len((results[n] or {}).get("interpretation", "")) < MIN_LEN
        ]
    else:
        todo = [n for n in numbers if n not in results]
    if not todo:
        print("没有需要生成的条目")
        return 0

    print(f"模型 {MODEL} | 并发 {WORKERS} | 待生成 {len(todo)} 条")
    failures: list[tuple[str, str]] = []

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(_work, n, source[n]): n for n in todo}
        for future in as_completed(futures):
            number = futures[future]
            try:
                num, interpretation, review = future.result()
                entry = dict(source[number])
                entry["interpretation"] = interpretation
                entry["_fortune_review"] = review
                results[num] = entry
            except Exception as exc:  # noqa: BLE001
                failures.append((number, str(exc)[:120]))
            with _lock:
                global _done
                _done += 1
                if _done % 10 == 0 or _done == len(todo):
                    print(f"  进度 {_done}/{len(todo)}（失败 {len(failures)}）", flush=True)

    ordered = {k: results[k] for k in sorted(results, key=lambda x: int(x))}
    OUT.write_text(
        json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n写入 {OUT}（{len(ordered)} 条，{OUT.stat().st_size:,} 字节）")
    if failures:
        print(f"失败 {len(failures)} 条：")
        for n, err in failures[:10]:
            print(f"  第 {n} 签：{err}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
