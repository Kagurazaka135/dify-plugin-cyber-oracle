# -*- coding: utf-8 -*-
"""时间源：按优先级解析时区，返回 naive「墙上时间」。

优先级：tool 参数 > provider 凭据 > 容器环境变量 TZ > Asia/Shanghai

为什么要剥 tzinfo：zhdate 不接受 aware datetime（会抛
"can't subtract offset-naive and offset-aware datetimes"）。
插件容器默认是 UTC，直接 datetime.now() 会拿到比北京时间慢 8 小时的时间，
对按时间起卦的方法（梅花易数、小六壬）会算出完全不同的卦。
"""

import os
from datetime import datetime, timedelta, timezone

FALLBACK_TZ = "Asia/Shanghai"

# 没有 tzdata 时（如 Windows 开发机、slim 镜像）只有固定偏移可兜底，
# 否则 UTC 会被静默当成 +8，把"少 8 小时"这个 bug 藏起来。
_FIXED_OFFSETS = {
    "UTC": 0,
    "Etc/UTC": 0,
    "GMT": 0,
    "Asia/Shanghai": 8,
    "Asia/Chongqing": 8,
    "Asia/Harbin": 8,
    "PRC": 8,
}


def resolve_timezone(tool_parameters=None, credentials=None) -> str:
    """三级解析：tool 参数 > provider 凭据 > 环境变量 TZ > 兜底。"""
    if tool_parameters:
        tz = (tool_parameters.get("timezone") or "").strip()
        if tz:
            return tz
    if credentials:
        tz = (credentials.get("timezone") or "").strip()
        if tz:
            return tz
    tz = (os.environ.get("TZ") or "").strip()
    if tz:
        return tz
    return FALLBACK_TZ


def local_now(tz_name: str = FALLBACK_TZ) -> datetime:
    """返回目标时区的墙上时间，已剥离 tzinfo。

    环境缺 tzdata 时（Windows 开发机、slim 镜像）退化为固定偏移；
    未知时区名同样退化为东八区。
    """
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo(tz_name)).replace(tzinfo=None)
    except Exception:
        offset = _FIXED_OFFSETS.get(tz_name, _FIXED_OFFSETS[FALLBACK_TZ])
        return datetime.now(timezone(timedelta(hours=offset))).replace(tzinfo=None)


def now_from(tool, tool_parameters=None) -> datetime:
    """tool 是 Tool 实例，provider 凭据从 self.runtime.credentials 取。"""
    creds = getattr(getattr(tool, "runtime", None), "credentials", None)
    return local_now(resolve_timezone(tool_parameters, creds))
