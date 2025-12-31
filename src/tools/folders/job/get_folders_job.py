from __future__ import annotations

from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "folders.job",
    "operation": "read",
    "tags": [],
    "http_method": "get",
    "http_path": "/v1/bulkJobs/{job_id}",
    "operation_id": "bulk-job-status",
}


def _serialize_job_status(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def get_folders_job(
    *,
    job_id: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Retrieve status of a bulk job (copy/move/rename folder).

    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.folders.job.get(job_id)
    response = _serialize_job_status(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="get_folders_job",
    description="When using this tool, always use the `filter_spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nThis API returns the status of a bulk job like copy and move folder operations.\n\n\n# Response Schema\n```json\n{\n  type: 'object',\n  properties: {\n    jobId: {\n      type: 'string',\n      description: 'Unique identifier of the bulk job.\\n'\n    },\n    purgeRequestId: {\n      type: 'string',\n      description: 'Unique identifier of the purge request. This will be present only if `purgeCache` is set to `true` in the rename folder API request.\\n'\n    },\n    status: {\n      type: 'string',\n      description: 'Status of the bulk job.',\n      enum: [        'Pending',\n        'Completed'\n      ]\n    },\n    type: {\n      type: 'string',\n      description: 'Type of the bulk job.',\n      enum: [        'COPY_FOLDER',\n        'MOVE_FOLDER',\n        'RENAME_FOLDER'\n      ]\n    }\n  }\n}\n```",
    inputSchema={
        "json": {
            "properties": {
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
                "job_id": {"type": "string"},
            },
            "required": ["job_id"],
            "type": "object",
        }
    },
)
async def get_folders_job_tool(
    job_id: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Retrieve status of a bulk job (copy/move/rename folder).

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await get_folders_job(
        job_id=job_id,
        filter_spec=filter_spec,
    )
