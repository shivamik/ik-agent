from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


DATE_FMT = "%Y-%m-%d"
MAX_RANGE_DAYS = 90
METADATA: Dict[str, Any] = {
    "resource": "accounts.usage",
    "operation": "read",
    "tags": [],
    "http_method": "get",
    "http_path": "/v1/accounts/usage",
    "operation_id": "get-usage",
}


def _parse_date(label: str, value: str) -> datetime:
    try:
        return datetime.strptime(value, DATE_FMT)
    except ValueError as exc:
        raise ValueError(f"{label} must be in YYYY-MM-DD format") from exc


def _validate_dates(start_date: str, end_date: str) -> None:
    start = _parse_date("start_date", start_date)
    end = _parse_date("end_date", end_date)

    if end <= start:
        raise ValueError("end_date must be after start_date")

    if (end - start).days >= MAX_RANGE_DAYS:
        raise ValueError(f"Date range must be less than {MAX_RANGE_DAYS} days")


async def get_accounts_usage(
    *,
    client=CLIENT,
    start_date: str,
    end_date: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Get ImageKit account usage between two dates.

    - Dates must be YYYY-MM-DD
    - end_date is exclusive
    - Max range: 90 days (delta strictly less than 90)
    """
    _validate_dates(start_date, end_date)

    body = {
        "start_date": start_date,
        "end_date": end_date,
    }
    raw = await client.accounts.usage.get(**body)

    response = raw.dict()

    return maybe_filter(filter_spec, response)


@tool(
    name="get_accounts_usage",
    description="""
Get ImageKit account usage information between two dates.

Use `filter_spec` (glom spec) to reduce the response size.

Examples:
- "bandwidthBytes"
- { bandwidth: "bandwidthBytes", storage: "mediaLibraryStorageBytes" }

Dates:
- start_date: YYYY-MM-DD
- end_date: YYYY-MM-DD (exclusive)
- Max range: 90 days
""",
)
async def get_accounts_usage_tool(
    start_date: str,
    end_date: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Returns usage metrics like:
    - bandwidthBytes
    - mediaLibraryStorageBytes
    - originalCacheStorageBytes
    - videoProcessingUnitsCount
    - extensionUnitsCount
    """

    return await get_accounts_usage(
        client=CLIENT,
        start_date=start_date,
        end_date=end_date,
        filter_spec=filter_spec,
    )
