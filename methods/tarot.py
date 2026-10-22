# -*- coding: utf-8 -*-
"""塔罗牌占卜模块

对外接口：calculate(dt, question) -> dict
返回 dict 包含方法名、牌阵信息、抽牌结果、农历时间
"""

import random
import hashlib
from datetime import datetime

# ============================================================
# 牌阵定义
# ============================================================
SPREADS = {
    "单张卡": {
        "cards": 1,
        "positions": ["今日指引"],
    },
    "三张牌阵": {
        "cards": 3,
        "positions": ["过去", "现在", "未来"],
    },
    "凯尔特十字阵": {
        "cards": 10,
        "positions": [
            "现状", "挑战", "过去基础", "近期未来",
            "上方（意识）", "下方（潜意识）",
            "自我定位", "环境", "希望/恐惧", "最终结果",
        ],
    },
}

# ============================================================
# 大阿尔卡纳 Major Arcana（22张）
# ============================================================
MAJOR_ARCANA = [
    {"id": 0,  "name": "愚人",       "name_en": "The Fool",
     "meaning_upright": "新的开始、冒险、天真、无限可能",
     "meaning_reversed": "鲁莽、犹豫不决、错失机会、逃避现实"},
    {"id": 1,  "name": "魔术师",     "name_en": "The Magician",
     "meaning_upright": "能力集中、创造力、行动力、资源在手",
     "meaning_reversed": "能力不足、欺骗、滥用才华、计划受阻"},
    {"id": 2,  "name": "女祭司",     "name_en": "The High Priestess",
     "meaning_upright": "直觉、潜意识、内在智慧、等待时机",
     "meaning_reversed": "直觉被压抑、秘密被揭开、表面化"},
    {"id": 3,  "name": "女皇",       "name_en": "The Empress",
     "meaning_upright": "丰收、母性、滋养、创造力、自然之美",
     "meaning_reversed": "依赖、创造力枯竭、忽视自我、匮乏"},
    {"id": 4,  "name": "皇帝",       "name_en": "The Emperor",
     "meaning_upright": "秩序、权威、结构、掌控、父亲形象",
     "meaning_reversed": "暴政、失控、缺乏纪律、权威滥用"},
    {"id": 5,  "name": "教皇",       "name_en": "The Hierophant",
     "meaning_upright": "传统、信仰、导师、智慧传承、仪式",
     "meaning_reversed": "反叛、打破传统、僵化教条、盲目追随"},
    {"id": 6,  "name": "恋人",       "name_en": "The Lovers",
     "meaning_upright": "选择、价值观、爱情、结合、真诚",
     "meaning_reversed": "分离、错误选择、价值观冲突、不忠"},
    {"id": 7,  "name": "战车",       "name_en": "The Chariot",
     "meaning_upright": "意志力、胜利、克服冲突、坚定前行",
     "meaning_reversed": "失控、失败、方向混乱、被情绪压倒"},
    {"id": 8,  "name": "力量",       "name_en": "Strength",
     "meaning_upright": "内在力量、勇气、以柔克刚、耐心",
     "meaning_reversed": "软弱、自我怀疑、被欲望支配、失控"},
    {"id": 9,  "name": "隐士",       "name_en": "The Hermit",
     "meaning_upright": "内省、独处、寻找真理、导师指引",
     "meaning_reversed": "孤立、逃避、拒绝建议、迷失方向"},
    {"id": 10, "name": "命运之轮",   "name_en": "Wheel of Fortune",
     "meaning_upright": "变化、循环、机遇、命运转折、好运",
     "meaning_reversed": "厄运、抗拒变化、循环不顺、运气差"},
    {"id": 11, "name": "正义",       "name_en": "Justice",
     "meaning_upright": "因果、公平、真相、决策、法律事务",
     "meaning_reversed": "不公、逃避责任、偏见、因果未到"},
    {"id": 12, "name": "倒吊人",     "name_en": "The Hanged Man",
     "meaning_upright": "牺牲、换个角度、等待、臣服、顿悟",
     "meaning_reversed": "抗拒牺牲、停滞、浪费时间、不肯放手"},
    {"id": 13, "name": "死神",       "name_en": "Death",
     "meaning_upright": "结束、新生、放下、蜕变、自然轮回",
     "meaning_reversed": "抗拒改变、卡住、恐惧结束、执着过去"},
    {"id": 14, "name": "节制",       "name_en": "Temperance",
     "meaning_upright": "平衡、调和、适度、耐心、融合",
     "meaning_reversed": "失衡、过度、缺乏节制、冲突"},
    {"id": 15, "name": "恶魔",       "name_en": "The Devil",
     "meaning_upright": "束缚、欲望、物质主义、执念、沉迷",
     "meaning_reversed": "挣脱束缚、觉醒、摆脱依赖、重新掌控"},
    {"id": 16, "name": "高塔",       "name_en": "The Tower",
     "meaning_upright": "崩塌、剧变、觉醒、真相揭露、推倒重来",
     "meaning_reversed": "逃避灾难、延缓崩塌、勉强维持、拒绝觉醒"},
    {"id": 17, "name": "星星",       "name_en": "The Star",
     "meaning_upright": "希望、疗愈、平静、灵感、信心恢复",
     "meaning_reversed": "绝望、失去信心、自我否定、灵感枯竭"},
    {"id": 18, "name": "月亮",       "name_en": "The Moon",
     "meaning_upright": "恐惧、幻觉、潜意识深处、迷惑、不安",
     "meaning_reversed": "恐惧消散、真相浮现、走出迷雾"},
    {"id": 19, "name": "太阳",       "name_en": "The Sun",
     "meaning_upright": "成功、喜悦、生命力、温暖、成就、童真",
     "meaning_reversed": "暂时的挫折、被遮蔽的快乐、过度乐观"},
    {"id": 20, "name": "审判",       "name_en": "Judgement",
     "meaning_upright": "觉醒、复活、召唤、清算、重新出发",
     "meaning_reversed": "逃避审判、自我怀疑、不愿面对、错过召唤"},
    {"id": 21, "name": "世界",       "name_en": "The World",
     "meaning_upright": "完成、圆满、整合、达成目标、旅途终点",
     "meaning_reversed": "未完成、拖延、不圆满、最后一里路"},
]

# ============================================================
# 小阿尔卡纳 Minor Arcana（56张）
# ============================================================
SUIT_NAMES = {
    "wands":     "权杖",
    "cups":      "圣杯",
    "swords":    "宝剑",
    "pentacles": "星币",
}

SUIT_ELEMENTS = {
    "wands":     "火",
    "cups":      "水",
    "swords":    "风",
    "pentacles": "土",
}

SUIT_THEMES = {
    "wands":     "行动、激情、事业、创造力",
    "cups":      "情感、关系、直觉、内心世界",
    "swords":    "思维、冲突、真相、沟通",
    "pentacles": "物质、工作、健康、现实生活",
}

COURT_TITLES = {11: "侍从", 12: "骑士", 13: "王后", 14: "国王"}
COURT_TITLES_EN = {11: "Page", 12: "Knight", 13: "Queen", 14: "King"}
NUMBER_NAMES_EN = {1: "Ace", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
                   6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten"}
SUIT_NAMES_EN = {"wands": "Wands", "cups": "Cups", "swords": "Swords", "pentacles": "Pentacles"}

# 每张小牌的含义：{suit: {number: (name_suffix, meaning_upright, meaning_reversed)}}
MINOR_ARCANA_MEANINGS = {
    "wands": {
        1:  ("一 (Ace)", "新的开始、灵感迸发、创造性的能量与热情", "计划延迟、缺乏方向、错失起点"),
        2:  ("二", "规划未来、做出选择、个人力量与远见", "犹豫不决、害怕改变、计划受阻"),
        3:  ("三", "远航、扩张视野、初步成功与探索", "计划受挫、失望、准备不足"),
        4:  ("四", "庆祝、稳固基础、和谐共处", "紧张不安、短暂和平、根基不稳"),
        5:  ("五", "竞争、冲突、在斗争中成长", "内耗、回避冲突、恶性竞争"),
        6:  ("六", "胜利、获得认可、凯旋归来", "失败、骄傲自满、他人不认可"),
        7:  ("七", "坚守立场、防御、孤胆勇气", "动摇投降、被压垮、孤立无援"),
        8:  ("八", "快速行动、消息来临、旅行", "停滞延误、计划混乱、冲动误事"),
        9:  ("九", "坚韧、最后的坚持、内在力量", "固执己见、精疲力竭、快要放弃"),
        10: ("十", "负担过重、压力到顶、责任在肩", "释放负担、推卸责任、终于卸下"),
        11: ("侍从", "探索、好消息、新冒险的好奇心", "幼稚冲动、坏消息、缺乏计划"),
        12: ("骑士", "热情冲动、冒险精神、快速推进", "急躁鲁莽、半途而废、不计后果"),
        13: ("王后", "自信、领导魅力、温暖掌控", "控制欲强、嫉妒、缺乏安全感"),
        14: ("国王", "创业精神、领袖远见、大局在握", "暴政独裁、缺乏方向、滥用权力"),
    },
    "cups": {
        1:  ("一 (Ace)", "新的感情、直觉开启、灵性萌芽", "情感空虚、失去爱、内心封闭"),
        2:  ("二", "结合、伴侣关系、和谐共处", "分离、失衡、信任破裂"),
        3:  ("三", "庆祝、友谊、集体欢乐时光", "过度放纵、孤独、背后流言"),
        4:  ("四", "冥想沉思、内心不满、重新审视", "觉醒觉悟、新的动力、走出低谷"),
        5:  ("五", "失去、悲伤、遗憾与惋惜", "接受现实、释怀放下、重拾希望"),
        6:  ("六", "回忆往昔、乡愁、童年怀旧", "沉溺过去、无法前行、被困在回忆"),
        7:  ("七", "幻想、多重选择、白日梦", "清醒抉择、脚踏实地、聚焦现实"),
        8:  ("八", "离开放手、寻找更高意义", "恐惧改变、停滞不前、执念难放"),
        9:  ("九", "愿望成真、满足幸福、美梦实现", "愿望落空、不满现状、贪得无厌"),
        10: ("十", "家庭幸福、情感圆满、爱的归宿", "家庭不和、情感破裂、离散"),
        11: ("侍从", "创意灵感、直觉敏锐、情感消息", "情感不成熟、坏消息、逃避"),
        12: ("骑士", "浪漫追求、魅力四射、主动出击", "花心不专、欺骗、情绪泛滥"),
        13: ("王后", "同理心、直觉滋养、情感成熟", "依赖心理、情感操纵、失去自我"),
        14: ("国王", "情感掌控、成熟外交、慈爱威严", "情绪勒索、冷漠疏离、失去控制"),
    },
    "swords": {
        1:  ("一 (Ace)", "清晰思维、真相突破、理智之光", "思维混乱、误解、信息不实"),
        2:  ("二", "抉择两难、僵局、需要权衡", "做出选择、打破僵局、放下纠结"),
        3:  ("三", "心碎、悲伤、背叛之痛", "释怀恢复、原谅放下、暗夜将尽"),
        4:  ("四", "休息恢复、静思冥想、暂退", "焦躁不安、无法休息、重返战场"),
        5:  ("五", "狭隘胜利、损人利己、冲突", "和解、选择和平、虽败犹荣"),
        6:  ("六", "过渡期、离开困境、向前看", "停滞不前、无法离开、陷入泥潭"),
        7:  ("七", "策略计谋、暗中行动、小聪明", "暴露真相、弄巧成拙、机关算尽"),
        8:  ("八", "束缚限制、无力感、被困住", "释放解脱、获得力量、挣脱限制"),
        9:  ("九", "焦虑噩梦、过度担忧、内心折磨", "释然希望、放下担忧、恐慌消退"),
        10: ("十", "彻底背叛、最低点、结束", "好转重生、触底反弹、释怀"),
        11: ("侍从", "警觉敏锐、批判思维、追寻真相", "鲁莽轻率、流言蜚语、思维混乱"),
        12: ("骑士", "果决行动、直面冲突、砍断乱麻", "冲动鲁莽、无谋之勇、伤人伤己"),
        13: ("王后", "洞察独立、凌厉智慧、边界清晰", "刻薄孤独、冷漠无情、精明过度"),
        14: ("国王", "权威理性、法律秩序、客观公正", "暴政操纵、不公审判、滥用逻辑"),
    },
    "pentacles": {
        1:  ("一 (Ace)", "新机会、财务起点、种子萌芽", "错失机会、财务延迟、投资落空"),
        2:  ("二", "平衡兼顾、多任务执行、灵活应变", "失衡、超负荷、财务紧张"),
        3:  ("三", "团队合作、技艺精湛、奠基立业", "各自为政、缺乏合作、散兵游勇"),
        4:  ("四", "守财稳固、控制欲、安全感", "贪婪吝啬、失去控制、财务恐慌"),
        5:  ("五", "物质困难、感到匮乏、被遗弃", "好转慰藉、精神富足、守望相助"),
        6:  ("六", "给予分享、慷慨大方、施与受", "自私债务、被施舍、不平等"),
        7:  ("七", "耐心等待、耕耘评估、静待花开", "焦虑不耐、投入无回报、拔苗助长"),
        8:  ("八", "勤奋精进、技能积累、专注打磨", "倦怠缺乏动力、粗制滥造、机械化"),
        9:  ("九", "富足独立、享受成果、财务自由", "过度依赖、财务挫折、挥霍"),
        10: ("十", "财富传承、家族积累、厚德载物", "财务困境、遗产纠纷、富不过三代"),
        11: ("侍从", "学习务实、新技能、脚踏实地", "不求上进、坏消息、眼高手低"),
        12: ("骑士", "勤奋可靠、高效务实、坚持", "懒惰停滞、无趣单调、缺少冲劲"),
        13: ("王后", "滋养务实、慷慨持家、稳重大方", "忽视财务、不善理财、过度依赖"),
        14: ("国王", "财富成就、经营稳健、基业长青", "贪婪腐败、守财奴、为富不仁"),
    },
}


def _build_deck() -> list:
    """构建完整 78 张塔罗牌组"""
    deck = []
    for card in MAJOR_ARCANA:
        deck.append({
            "id": f"major_{card['id']}",
            "name": card["name"],
            "name_en": card["name_en"],
            "type": "major",
            "suit": None,
            "suit_name": None,
            "element": None,
            "number": card["id"],
            "meaning_upright": card["meaning_upright"],
            "meaning_reversed": card["meaning_reversed"],
            "court_title": None,
        })
    for suit_key, suit_name in SUIT_NAMES.items():
        for num in range(1, 15):
            suffix, up, rev = MINOR_ARCANA_MEANINGS[suit_key][num]
            court_title = None
            if num >= 11:
                court_title = COURT_TITLES[num]
                card_num = num
            else:
                card_num = num
            en_suit = SUIT_NAMES_EN[suit_key]
            if num >= 11:
                en_name = f"{COURT_TITLES_EN[num]} of {en_suit}"
            else:
                en_name = f"{NUMBER_NAMES_EN[num]} of {en_suit}"
            deck.append({
                "id": f"{suit_key}_{num}",
                "name": f"{suit_name}{suffix}",
                "name_en": en_name,
                "type": "minor",
                "suit": suit_key,
                "suit_name": suit_name,
                "element": SUIT_ELEMENTS[suit_key],
                "number": card_num,
                "meaning_upright": up,
                "meaning_reversed": rev,
                "court_title": court_title,
            })
    return deck


def _seed_from_string(s: str) -> int:
    """将字符串转换为稳定的随机种子"""
    return int(hashlib.md5(s.encode("utf-8")).hexdigest()[:8], 16)


def shuffle_and_draw(spread_name: str, seed_text: str = "") -> tuple:
    """
    洗牌并抽取指定牌阵的牌。
    返回 (drawn_cards, spread_info)
    drawn_cards 是列表，每项是 card dict 加上 position 和 upright 字段
    """
    deck = _build_deck()
    rng = random.Random()
    if seed_text:
        rng.seed(_seed_from_string(seed_text))

    rng.shuffle(deck)

    if spread_name not in SPREADS:
        raise ValueError(f"未知牌阵：{spread_name}，可选：{list(SPREADS.keys())}")

    spread = SPREADS[spread_name]
    drawn = []
    for i in range(spread["cards"]):
        card = deck[i].copy()
        card["upright"] = rng.choice([True, False])
        card["position"] = spread["positions"][i]
        drawn.append(card)

    return drawn, spread


def calculate(dt: datetime, question: str, seed=None, spread_name="三张牌阵") -> dict:
    """
    塔罗牌占卜入口。
    参数：
        dt: 公历时间（用于显示，不参与核心计算）
        question: 用户问题（用作随机种子，连接"能量"）
        seed: 可复现种子；为 None 时沿用原逻辑（question + dt 拼 seed_text）
        spread_name: 牌阵名，默认"三张牌阵"
    返回：
        dict 包含方法名、牌阵信息、抽牌结果、农历时间
    """
    if seed is not None:
        seed_text = str(seed)
    else:
        seed_text = f"{question}||{dt.isoformat()}"

    drawn, spread = shuffle_and_draw(spread_name, seed_text)

    # 获取农历时间信息（用于展示）
    try:
        from utils.lunar import get_lunar_info
        lunar = get_lunar_info(dt)
    except Exception:
        lunar = {
            "lunar_year": dt.year,
            "lunar_month": dt.month,
            "lunar_day": dt.day,
            "year_ganzhi": "",
            "shichen_order": 0,
            "shichen_name": "",
            "day_ganzhi": "",
            "hour": dt.hour,
            "datetime": dt,
        }

    return {
        "method": "塔罗牌",
        "spread_name": spread_name,
        "spread": spread,
        "cards": drawn,
        "lunar": lunar,
        "question": question,
    }
