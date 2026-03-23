from __future__ import annotations

import re
from datetime import datetime
from datetime import timedelta, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo

    IST = ZoneInfo("Asia/Kolkata")
except Exception:
    IST = timezone(timedelta(hours=5, minutes=30))


def now_ist() -> datetime:
    return datetime.now(tz=IST)


def now_ist_iso() -> str:
    return now_ist().isoformat()


def slugify_name(value: str) -> str:
    text = Path(value).stem.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")
