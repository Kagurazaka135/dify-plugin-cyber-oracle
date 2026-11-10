# -*- coding: utf-8 -*-
"""自动选法：按问题内容挑选最合适的占卜方法。

对外接口：route(question) -> dict
返回 dict 包含 key / name / topic / reason / scores / question。

关键词按"越具体越优先"排列：先看是不是找东西、出门平安，再看感情、钱财，
最后才落到通用的决策问题。

打分 = 命中关键词的字数累加 × 该方法的位置权重（排越前权重越高）。
单纯比字长会被通用词压过：比如「该不该跟他分手」里「该不该」(3 字) 比
「分手」(2 字) 长，不乘权重就会判成决策类，而这句话问的显然是感情。
"""

ROUTES = [
    {
        "key": "xiao_liu_ren",
        "name": "小六壬",
        "topic": "寻物",
        "keywords": [
            "丢了", "找不到", "遗失", "失物", "落在哪", "落哪",
            "忘在", "丢在", "不见了", "找不回来", "东西没",
        ],
    },
    {
        "key": "ling_qian",
        "name": "灵签（关帝）",
        "topic": "出行与平安",
        "keywords": [
            "出行", "出门", "远行", "旅行", "旅游", "搬家", "平安",
            "顺利", "路上", "考试", "比赛", "手术", "住院", "求平安",
        ],
    },
    {
        "key": "tarot",
        "name": "塔罗牌占卜",
        "topic": "感情",
        "keywords": [
            "感情", "爱情", "复合", "分手", "相亲", "暧昧", "喜欢",
            "暗恋", "恋爱", "男朋友", "女朋友", "对象", "结婚", "婚姻",
            "桃花", "缘分", "表白", "异地恋",
        ],
    },
    {
        "key": "coin_hexagram",
        "name": "金钱卦",
        "topic": "财务",
        "keywords": [
            "财运", "钱", "投资", "生意", "股票", "理财", "赚钱",
            "收入", "工资", "买卖", "亏", "赚", "报价", "合同", "存款",
        ],
    },
    {
        "key": "plum_blossom",
        "name": "梅花易数",
        "topic": "决策",
        "keywords": [
            "要不要", "该不该", "是否", "能不能", "选择", "决定",
            "跳槽", "辞职", "工作", "面试", "offer", "机会",
            "去不去", "做不做", "值不值",
        ],
    },
]

DEFAULT_KEY = "plum_blossom"


def _score(question: str):
    """返回 (加权分, 原始分, 命中词)，原始分保留下来方便排查判定。"""
    weighted = {}
    raw = {}
    hits = {}
    for index, item in enumerate(ROUTES):
        matched = [keyword for keyword in item["keywords"] if keyword in question]
        hits[item["key"]] = matched
        raw[item["key"]] = sum(len(keyword) for keyword in matched)
        weighted[item["key"]] = raw[item["key"]] * (len(ROUTES) - index)
    return weighted, raw, hits


def route(question: str) -> dict:
    text = (question or "").strip()
    weighted, raw, hits = _score(text)

    # max 在分数并列时取列表里靠前的那个，也就是优先级更高的具体类别
    best = max(ROUTES, key=lambda item: weighted[item["key"]])
    chosen = best if weighted[best["key"]] > 0 else next(
        item for item in ROUTES if item["key"] == DEFAULT_KEY
    )

    if weighted[chosen["key"]] > 0:
        matched = hits[chosen["key"]]
        reason = f"命中「{'、'.join(matched)}」，属于{chosen['topic']}类问题，用{chosen['name']}。"
    elif text:
        reason = f"没抓到明显指向，按当下时间起卦最稳，用{chosen['name']}。"
    else:
        reason = f"没填问题，按当下时间起卦最稳，用{chosen['name']}。"

    return {
        "key": chosen["key"],
        "name": chosen["name"],
        "topic": chosen["topic"],
        "reason": reason,
        "scores": raw,
        "question": text,
    }
