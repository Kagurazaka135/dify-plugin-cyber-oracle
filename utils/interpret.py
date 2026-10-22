# -*- coding: utf-8 -*-
"""可选 AI 解读模块：把 CLI 版 llm_module.py 的 7 套提示词接到 Dify 反向调用上。

提示词的结构与各方法原有措辞原样保留（R5）；调用方式从直连 API 改为
``session.model.llm.invoke`` 反向调用，插件内不持有任何 API Key（F6）。
"""

from dify_plugin.entities.model.message import SystemPromptMessage, UserPromptMessage


def _build_plum_blossom(result, question):
    lunar = result["lunar"]
    lunar_time = {
        "year": f"{lunar['year_ganzhi']}（{lunar['lunar_year']}）",
        "month": f"{lunar['lunar_month']}",
        "day": f"{lunar['lunar_day']}（{lunar['day_ganzhi']}）",
        "hour": lunar["shichen_name"],
    }
    og = result["original"]
    ch = result["changed"]
    dl = result["dynamic_line"]
    system = (
        "你是一位精通《周易》的命理大师。请按以下结构输出解读：\n"
        "一、卦象详解：用传统周易术语，分析本卦、变卦、动爻的卦象含义。\n"
        "二、白话解读：用现代口语、生活化的语言重新解释一遍，像朋友聊天一样，避免文言和术语，让人一看就懂。\n"
        "三、切实建议：给出具体、可操作的行动建议。\n"
        "最后赛博神棍的话，看看就行了。"
    )
    user = (
        f"起卦时间（农历）：{lunar_time['year']}年{lunar_time['month']}月"
        f"{lunar_time['day']}日{lunar_time['hour']}时\n"
        f"用户所问之事：{question}\n"
        f"本卦：{og['name']}（{og['symbol']}）\n"
        f"变卦：{ch['name']}（{ch['symbol']}）\n"
        f"动爻：第{dl}爻"
    )
    return system, user


def _build_tarot(result, question):
    cards = result["cards"]
    spread = result["spread"]

    card_lines = []
    for c in cards:
        orientation = "正位" if c["upright"] else "逆位"
        meaning = c["meaning_upright"] if c["upright"] else c["meaning_reversed"]
        suit_info = ""
        if c["type"] == "minor":
            suit_info = f" ({c['suit_name']}·{c['element']}元素)"
        card_lines.append(
            f"  [{c['position']}位置] {c['name']} ({c['name_en']}) — {orientation}{suit_info}\n"
            f"    牌义：{meaning}"
        )

    cards_text = "\n".join(card_lines)

    system = (
        "你是一位精通塔罗牌的占卜大师。请按以下结构输出解读：\n\n"
        "一、牌面详解：逐张解读每张牌在当前位置的含义（正位/逆位），"
        "结合牌的元素属性和用户提问，给出个性化分析。\n\n"
        "二、综合解读：将牌阵中所有牌联系起来，找出牌与牌之间的关联、"
        "矛盾和呼应，分析整体的能量趋势和内在逻辑。\n\n"
        "三、切实建议：给出具体、可操作的行动建议，帮助用户将牌阵的"
        "信息转化为实际生活中的行动。\n\n"
        "最后赛博神棍的话，看看就行了。"
        "注意：第一部分的牌面详解可以用专业术语和传统表达风格，但在综合解读和切实建议部分，切换成朋友聊天的语气——用自然段落、不用编号列表、不用小标题、不用加粗。就像你一边看着牌一边跟朋友面对面说话那样。"
    )
    user = (
        f"牌阵：{result.get('spread_name', '塔罗牌阵')}\n"
        f"抽牌数量：{spread['cards']} 张\n"
        f"用户所问之事：{question}\n\n"
        f"抽牌结果：\n{cards_text}"
    )
    return system, user


def _build_bone_weight(result, question):
    lunar = result["lunar"]
    weights = result["weights"]

    system = (
        "你是一位精通袁天罡称骨法的命理大师。请按以下结构输出解读：\n\n"
        "一、骨重解析：解释这个骨重在称骨法中的地位——是轻是重？落在什么段位？"
        "从2两到7两的分布中它处于什么位置？记住：称骨法有一个有趣的统计现象——"
        "四个独立分量的加总会让大部分人的骨重自然落在3两到5两之间，"
        "落在两端的（极轻/极重）在概率上本来就极少。\n\n"
        "二、批语白话：将称骨歌原文用现代口语重新表达，让用户一看就懂，"
        "像朋友聊天一样，避免文言术语。\n\n"
        "三、切实建议：根据骨重格局，给出具体的生活建议。"
        "但务必强调：命格只是底色，后天努力才是真正的画笔。"
        "骨重轻的人靠勤奋弥补，骨重重的人靠谦虚守住。"
        "称骨看个乐子，日子靠自己过。\n\n"
        "注意：用朋友聊天的语气，不要教条，可以适当幽默。"
    )
    user = (
        f"用户出生时间（公历）：{result['birth_dt']}\n"
        f"农历：{lunar['year_ganzhi']}年{lunar['lunar_month']}月"
        f"{lunar['lunar_day']}日 {lunar['shichen_name']}时\n"
        f"性别：{result['gender']}\n"
        f"四柱重量：年柱{weights['year']}钱 + 月柱{weights['month']}钱"
        f" + 日柱{weights['day']}钱 + 时柱{weights['hour']}钱"
        f" = 总骨重{result['bone_weight']}（{weights['total']}钱）\n"
        f"称骨歌批语原文：{result['poem']}\n"
        + (f"用户所问之事：{question}" if question else "")
    )
    return system, user


def _build_zhuge_qian(result, question):
    qd = result["qian_data"]
    inp = result["input"]
    chars_text = "".join(inp["chars"])

    system = (
        "你是一位精通诸葛神数的解签大师。请按以下结构输出解读：\n\n"
        "一、签文详解：解读签诗的含义，分析签名的意象。"
        "诸葛神数共384签，每签的签诗都是一首七言绝句，"
        "蕴含传统命理智慧。请结合签诗本身进行分析。\n\n"
        "二、与字关联：用户所报的三个字带有自身意念，"
        "请将三个字的意象与签诗内容相互印证，"
        "找出字与签之间的呼应关系。\n\n"
        "三、白话解读：用现代口语、生活化的语言重新解释一遍，"
        "像朋友聊天一样，避免文言和术语，让人一看就懂。\n\n"
        "四、切实建议：给出具体、可操作的行动建议。\n\n"
        "最后提醒：赛博神棍的话，看看就行了，别太当真。"
    )
    user = (
        f"用户所报三个字：{chars_text}\n"
        f"康熙笔画数：{inp['strokes']}\n"
        f"求得 —— 第 {result['qian_number']} 签：{qd['title']}\n"
        f"签诗：\n{qd['poem']}\n"
        f"签文断语：{qd['interpretation']}\n"
        + (f"\n用户所问之事：{question}" if question else "")
    )
    return system, user


def _build_xiao_liu_ren(result, question):
    lunar = result["lunar"]
    final = result["final"]
    steps = result["steps"]
    system = (
        "你擅长用小六壬作生活化解读。请结合用户的问题与掌诀落位，"
        "给出自然、温和、具体的分析和建议；不要复述掌诀原文，也不要把占卜说成确定事实。"
    )
    user = (
        f"用户的问题：{question or '一般指引'}\n"
        f"农历时间：{lunar['lunar_month']}月{lunar['lunar_day']}日"
        f"{lunar['shichen_name']}时\n"
        f"推算落位：月{steps['month']}、日{steps['day']}、时{steps['hour']}\n"
        f"最终掌诀：{final['name']}（{final['luck']}）\n"
        f"断辞参考：{final['fortune']}\n"
        f"相关事项：事业{final['career']}；感情{final['love']}；"
        f"健康{final['health']}；失物{final['lost']}；出行{final['travel']}"
    )
    return system, user


def _build_ling_qian(result, question):
    qian = result["qian_data"]
    system = (
        "你擅长解读关帝灵签。请结合用户的问题、签的吉凶与意象，"
        "用自然的朋友式语气给出有分寸的分析和可行建议；不要复述或逐句改写签诗、断语，"
        "也不要把签意说成确定预言。"
    )
    user = (
        f"用户的问题：{question or '一般指引'}\n"
        f"签号：{result['qian_number']}（{qian['title']}）\n"
        f"吉凶：{qian['grade']}\n"
        f"签诗：{qian['poem']}\n"
        f"断语：{qian['interpretation']}\n"
        f"关键词：{'、'.join(qian.get('keywords', []))}"
    )
    return system, user


def _build_coin_hexagram(result, question):
    original = result["original"]
    changed = result["changed"]
    moving_lines = result["moving_lines"]
    line_text = "\n".join(
        f"第{line['position']}爻 {line['name']}：{line['scripture']}"
        for line in result["lines"] if line["moving"]
    ) or "无动爻，为静卦"
    changed_text = (
        f"{changed['name']}（{changed['symbol']}），卦辞：{changed['scripture']}"
        if changed is not None else "无变卦"
    )
    system = (
        "你擅长用周易卦象作自然、审慎的生活化解读。请结合用户问题、本卦、变卦和动爻，"
        "说明趋势与可执行建议；不要复述或逐句改写卦辞爻辞，也不要断言未来必然如此。"
    )
    user = (
        f"用户的问题：{question or '一般指引'}\n"
        f"本卦：{original['name']}（{original['symbol']}），卦辞：{original['scripture']}\n"
        f"变卦：{changed_text}\n"
        f"动爻：{'、'.join(map(str, moving_lines)) or '无'}\n"
        f"动爻爻辞：\n{line_text}"
    )
    return system, user


_BUILDERS = {
    "plum_blossom": _build_plum_blossom,
    "tarot": _build_tarot,
    "bone_weight": _build_bone_weight,
    "zhuge_qian": _build_zhuge_qian,
    "xiao_liu_ren": _build_xiao_liu_ren,
    "ling_qian": _build_ling_qian,
    "coin_hexagram": _build_coin_hexagram,
}


def build_prompt(method_key, result, question):
    """按 method_key 选提示词，返回 (system_prompt, user_prompt)。"""
    builder = _BUILDERS.get(method_key)
    if builder is None:
        raise ValueError(f"未知的解读方法：{method_key}")
    return builder(result, question)


def interpret(tool, model_cfg, method_key, result, question) -> str:
    """tool 是当前 Tool 实例（提供 session），method_key 决定用哪套提示词。"""
    system, user = build_prompt(method_key, result, question)
    messages = [SystemPromptMessage(content=system), UserPromptMessage(content=user)]
    resp = tool.session.model.llm.invoke(
        model_config=model_cfg,
        prompt_messages=messages,
        stream=False,
    )
    return (resp.message.content or "").strip()
