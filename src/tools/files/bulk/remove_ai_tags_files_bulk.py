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
    "http_path": "/v1/files/removeAITags",
    "operation_id": "remove-ai-tags-bulk",
}


def _serialize_bulk_remove_ai_tags(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def remove_ai_tags_files_bulk(
    *,
    ai_tags: Sequence[str],
    file_ids: Sequence[str],
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Remove AI tags from multiple files in bulk.

    - Up to 50 file IDs can be specified per request.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.files.bulk.remove_ai_tags(
        ai_tags=list(ai_tags),
        file_ids=list(file_ids),
    )
    response = _serialize_bulk_remove_ai_tags(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="remove_ai_tags_files_bulk",
    description="When using this tool, always use the `filter_spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nThis API removes AITags from multiple files in bulk. A maximum of 50 files can be specified at a time.\n\n\n# Response Schema\n```json\n{\n  type: 'object',\n  properties: {\n    successfullyUpdatedFileIds: {\n      type: 'array',\n      description: 'An array of fileIds that in which AITags were successfully removed.\\n',\n      items: {\n        type: 'string'\n      }\n    }\n  }\n}\n```",
    inputSchema={
        "json": {
            "properties": {
                "ai_tags": {
                    "description": "An array of ai_tags that you want to remove "
                    "from the files.\n",
                    "items": {"type": "string"},
                    "type": "array",
                },
                "file_ids": {
                    "description": "An array of fileIds from which you want to "
                    "remove ai_tags.\n",
                    "items": {"type": "string"},
                    "type": "array",
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
            },
            "required": ["ai_tags", "file_ids"],
            "type": "object",
        }
    },
)
async def remove_ai_tags_files_bulk_tool(
    ai_tags: Sequence[str],
    file_ids: Sequence[str],
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Remove AI tags from multiple files in bulk.

    Provide up to 50 file IDs per request.

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await remove_ai_tags_files_bulk(
        ai_tags=ai_tags,
        file_ids=file_ids,
        filter_spec=filter_spec,
    )
