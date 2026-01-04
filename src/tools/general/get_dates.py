from datetime import datetime, timezone
from typing import Any, Dict, Optional

from strands import tool


def _format_datetime(value: datetime, fmt: Optional[str]) -> str:
    if fmt:
        return value.strftime(fmt)
    return value.isoformat()


async def get_dates(
    *,
    format: Optional[str] = None,
) -> Dict[str, str]:
    """
    Return current local and UTC dates/times.
    """
    now_local = datetime.now().astimezone()
    now_utc = datetime.now(timezone.utc)

    return {
        "local_date": _format_datetime(now_local, "%Y-%m-%d"),
        "local_time": _format_datetime(now_local, "%H:%M:%S"),
        "local_datetime": _format_datetime(now_local, format),
        "utc_date": _format_datetime(now_utc, "%Y-%m-%d"),
        "utc_time": _format_datetime(now_utc, "%H:%M:%S"),
        "utc_datetime": _format_datetime(now_utc, format),
    }


@tool(
    name="get_dates",
    description="Return current local/UTC date and time strings.",
)
async def get_dates_tool(
    format: Optional[str] = None,
) -> Dict[str, str]:
    """
    Return current local and UTC date/time strings.

    Provide an optional strftime `format` to override datetime formatting.
    """
    return await get_dates(format=format)
