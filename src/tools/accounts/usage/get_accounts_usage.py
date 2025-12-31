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
    raw = await CLIENT.accounts.usage.get(**body)

    response = raw.dict()

    return maybe_filter(filter_spec, response)


@tool(
    name="get_accounts_usage",
    description="When using this tool, always use the `filter_spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nGet the account usage information between two dates. Note that the API response includes data from the start date while excluding data from the end date. In other words, the data covers the period starting from the specified start date up to, but not including, the end date.\n\n\n# Response Schema\n```json\n{\n  type: 'object',\n  properties: {\n    bandwidthBytes: {\n      type: 'integer',\n      description: 'Amount of bandwidth used in bytes.'\n    },\n    extensionUnitsCount: {\n      type: 'integer',\n      description: 'Number of extension units used.'\n    },\n    mediaLibraryStorageBytes: {\n      type: 'integer',\n      description: 'Storage used by media library in bytes.'\n    },\n    originalCacheStorageBytes: {\n      type: 'integer',\n      description: 'Storage used by the original cache in bytes.'\n    },\n    videoProcessingUnitsCount: {\n      type: 'integer',\n      description: 'Number of video processing units used.'\n    }\n  }\n}\n```",
    inputSchema={
        "json": {
            "properties": {
                "end_date": {
                    "description": "Specify a `endDate` in `YYYY-MM-DD` format. "
                    "It should be after the `startDate`. The "
                    "difference between `startDate` and `endDate` "
                    "should be less than 90 days.",
                    "format": "date",
                    "type": "string",
                },
                "filter_spec": {
                    "description": "A filter_spec to apply to the response to "
                    "include certain fields. Consult the "
                    "output schema in the tool description to "
                    "see the fields that are available.\n"
                    "\n"
                    "For example: to include only the `name` "
                    "field in every object of a results array, "
                    'you can provide ".results[].name".\n'
                    "\n"
                    "For more information, see the [jq "
                    "documentation](https://jqlang.org/manual/).",
                    "title": "filter_spec",
                    "type": "string",
                },
                "start_date": {
                    "description": "Specify a `startDate` in `YYYY-MM-DD` "
                    "format. It should be before the `endDate`. "
                    "The difference between `startDate` and "
                    "`endDate` should be less than 90 days.",
                    "format": "date",
                    "type": "string",
                },
            },
            "required": ["end_date", "start_date"],
            "type": "object",
        }
    },
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
        start_date=start_date,
        end_date=end_date,
        filter_spec=filter_spec,
    )
