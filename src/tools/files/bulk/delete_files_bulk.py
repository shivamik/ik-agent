from typing import Any, Dict, Optional, Sequence

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "files.bulk",
    "operation": "write",
    "tags": [],
    "http_method": "post",
    "http_path": "/v1/files/batch/deleteByFileIds",
    "operation_id": "delete-multiple-files",
}


def _serialize_bulk_delete(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def delete_files_bulk(
    *,
    file_ids: Sequence[str],
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Delete multiple files and all their versions permanently.

    - Up to 100 file IDs can be specified per request.
    - Deleting a file does not purge cache; use cache invalidation separately.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.files.bulk.delete(file_ids=list(file_ids))
    response = _serialize_bulk_delete(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="delete_files_bulk",
    description="When using this tool, always use the `filter_spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nThis API deletes multiple files and all their file versions permanently.\n\nNote: If a file or specific transformation has been requested in the past, then the response is cached. Deleting a file does not purge the cache. You can purge the cache using purge cache API.\n\nA maximum of 100 files can be deleted at a time.\n\n\n# Response Schema\n```json\n{\n  type: 'object',\n  properties: {\n    successfullyDeletedFileIds: {\n      type: 'array',\n      description: 'An array of fileIds that were successfully deleted.\\n',\n      items: {\n        type: 'string'\n      }\n    }\n  }\n}\n```",
    inputSchema={
        "json": {
            "properties": {
                "file_ids": {
                    "description": "An array of fileIds which you want to delete.\n",
                    "items": {"type": "string"},
                    "type": "array",
                },
                "filter_spec": {
                    "description": "A glom spec to apply to the response to "
                    "include certain fields. Consult the output "
                    "schema in the tool description to see the "
                    "fields that are available.\n"
                    "\n"
                    "For example: to include only the `name` "
                    "field in every object of a results array, "
                    'you can provide ".results[].name".\n'
                    "\n"
                    "For more information, see the [glom"
                    "documentation](http://glom.readthedocs.io/).",
                    "title": "glom spec",
                    "type": "string",
                },
            },
            "required": ["file_ids"],
            "type": "object",
        }
    },
)
async def delete_files_bulk_tool(
    file_ids: Sequence[str],
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Delete multiple files and all their versions permanently.

    Provide up to 100 file IDs per request. This does not purge cache.

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await delete_files_bulk(
        file_ids=file_ids,
        filter_spec=filter_spec,
    )
