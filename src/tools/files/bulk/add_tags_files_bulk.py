from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "files.bulk",
    "operation": "write",
    "tags": [],
    "http_method": "post",
    "http_path": "/v1/files/addTags",
    "operation_id": "add-tags-bulk",
}


def _serialize_bulk_add_tags(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def add_tags_files_bulk(
    *,
    file_ids: Sequence[str],
    tags: Sequence[str],
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Add tags to multiple files in bulk.

    - Up to 50 file IDs can be specified per request.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.files.bulk.add_tags(
        file_ids=list(file_ids),
        tags=list(tags),
    )
    response = _serialize_bulk_add_tags(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="add_tags_files_bulk",
    description="When using this tool, always use the `filter_spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nThis API adds tags to multiple files in bulk. A maximum of 50 files can be specified at a time.\n\n\n# Response Schema\n```json\n{\n  type: 'object',\n  properties: {\n    successfullyUpdatedFileIds: {\n      type: 'array',\n      description: 'An array of fileIds that in which tags were successfully added.\\n',\n      items: {\n        type: 'string'\n      }\n    }\n  }\n}\n```",
    inputSchema={
        "json": {
            "type": "object",
            "properties": {
                "fileIds": {
                    "type": "array",
                    "description": "An array of fileIds to which you want to add tags.\n",
                    "items": {
                        "type": "string",
                    },
                },
                "tags": {
                    "type": "array",
                    "description": "An array of tags that you want to add to the files.\n",
                    "items": {
                        "type": "string",
                    },
                },
                "jq_filter": {
                    "type": "string",
                    "title": "jq Filter",
                    "description": 'A jq filter to apply to the response to include certain fields. Consult the output schema in the tool description to see the fields that are available.\n\nFor example: to include only the `name` field in every object of a results array, you can provide ".results[].name".\n\nFor more information, see the [jq documentation](https://jqlang.org/manual/).',
                },
            },
            "required": ["fileIds", "tags"],
        }
    },
)
async def add_tags_files_bulk_tool(
    file_ids: Sequence[str],
    tags: Sequence[str],
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Add tags to multiple files in bulk.

    Provide up to 50 file IDs per request.

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await add_tags_files_bulk(
        file_ids=file_ids,
        tags=tags,
        filter_spec=filter_spec,
    )
