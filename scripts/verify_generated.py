# -*- coding: utf-8 -*-
"""校验生成的解读数据，并报告吉凶复核冲突。

用法：
    python verify_generated.py
    python verify_generated.py --apply   # 校验通过后替换 data/zhuge_qian.json

替换会做三件事：
    1. 去掉 _fortune_review（校对字段不随包发布）
    2. 保留其余字段原样
    3. 备份原文件为 zhuge_qian.json.bak
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "data" / "zhuge_qian_generated.json"
DST = ROOT / "data" / "zhuge_qian.json"

REQUIRED = ("number", "title", "palace", "fortune", "poem", "verdict", "commentary")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="校验通过后替换正式数据")
    args = ap.parse_args()

    if not GEN.exists():
        print(f"[X] 找不到 {GEN}，先跑 gen_zhuge_interpretations.py")
        return 1

    data = json.loads(GEN.read_text(encoding="utf-8"))
    problems: list[str] = []

    if len(data) != 384:
        problems.append(f"条数应为 384，实际 {len(data)}")

    missing = [n for n in map(str, range(1, 385)) if n not in data]
    if missing:
        problems.append(f"缺签号：{missing[:10]}{'…' if len(missing) > 10 else ''}")

    empty = [n for n, v in data.items() if not (v.get("interpretation") or "").strip()]
    if empty:
        problems.append(f"空解读 {len(empty)} 条：{empty[:10]}")

    short = [n for n, v in data.items() if len(v.get("interpretation", "")) < 60]
    if short:
        problems.append(f"解读过短（<60 字）{len(short)} 条：{short[:10]}")

    for n, v in data.items():
        for key in REQUIRED:
            if key not in v:
                problems.append(f"第 {n} 签缺字段 {key}")

    lengths = [len(v.get("interpretation", "")) for v in data.values()]
    avg = sum(lengths) // len(lengths) if lengths else 0

    print(f"条数        : {len(data)}")
    print(f"空解读      : {len(empty)}")
    print(f"解读字数    : 最短 {min(lengths)} / 平均 {avg} / 最长 {max(lengths)}")

    conflicts = []
    for n, v in data.items():
        review = v.get("_fortune_review") or ""
        original = v.get("fortune") or ""
        if review and original and review != original:
            conflicts.append((n, original, review))
    print(f"吉凶复核冲突: {len(conflicts)} 条")
    for n, orig, rev in conflicts[:15]:
        print(f"    第 {n:>3} 签：原标注 {orig} → 复核 {rev}")

    if problems:
        print("\n[X] 校验未通过：")
        for p in problems:
            print(f"    - {p}")
        return 1

    print("\n[OK] 校验通过")

    if args.apply:
        backup = DST.with_suffix(".json.bak")
        if DST.exists():
            shutil.copy2(DST, backup)
            print(f"已备份原文件 → {backup.name}")
        cleaned = {
            n: {k: v for k, v in entry.items() if not k.startswith("_")}
            for n, entry in data.items()
        }
        DST.write_text(
            json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"已写入 {DST}（{DST.stat().st_size:,} 字节）")

    return 0


if __name__ == "__main__":
    sys.exit(main())
