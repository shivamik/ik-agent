from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "files",
    "operation": "write",
    "tags": [],
    "http_method": "put",
    "http_path": "/v1/files/rename",
    "operation_id": "rename-file",
}


def _serialize_rename_result(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def rename_files(
    *,
    file_path: str,
    new_file_name: str,
    purge_cache: Optional[bool] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Rename a file and all of its versions.

    - Optionally purge cache for the old URL via purge_cache.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    body = {
        "file_path": file_path,
        "new_file_name": new_file_name,
        "purge_cache": purge_cache,
    }
    filtered_body = {k: v for k, v in body.items() if v is not None}

    raw = await CLIENT.files.rename(**filtered_body)
    response = _serialize_rename_result(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="rename_files",
    description="When using this tool, always use the `filter_spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nYou can rename an already existing file in the media library using rename file API. This operation would rename all file versions of the file. \n\nNote: The old URLs will stop working. The file/file version URLs cached on CDN will continue to work unless a purge is requested.\n\n\n# Response Schema\n```json\n{\n  type: 'object',\n  properties: {\n    purgeRequestId: {\n      type: 'string',\n      description: 'Unique identifier of the purge request. This can be used to check the status of the purge request.\\n'\n    }\n  }\n}\n```",
    inputSchema={
        "json": {
            "properties": {
                "file_path": {
                    "description": "The full path of the file you want to rename.\n",
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
                    "For more information, see the [glom"
                    "documentation](http://glom.readthedocs.io/).",
                    "title": "filter_spec",
                    "type": "string",
                },
                "new_file_name": {
                    "description": "The new name of the file. A filename "
                    "can contain:\n"
                    "\n"
                    "Alphanumeric Characters: `a-z`, `A-Z`, "
                    "`0-9` (including Unicode letters, "
                    "marks, and numerals in other "
                    "languages).\n"
                    "Special Characters: `.`, `_`, and `-`.\n"
                    "\n"
                    "Any other character, including space, "
                    "will be replaced by `_`.\n",
                    "type": "string",
                },
                "purge_cache": {
                    "description": "Option to purge cache for the old file "
                    "and its versions' URLs.\n"
                    "\n"
                    "When set to true, it will internally "
                    "issue a purge cache request on CDN to "
                    "remove cached content of old file and its "
                    "versions. This purge request is counted "
                    "against your monthly purge quota.\n"
                    "\n"
                    "Note: If the old file were accessible at "
                    "`https://ik.imagekit.io/demo/old-filename.jpg`, "
                    "a purge cache request would be issued "
                    "against "
                    "`https://ik.imagekit.io/demo/old-filename.jpg*` "
                    "(with a wildcard at the end). It will "
                    "remove the file and its versions' URLs "
                    "and any transformations made using query "
                    "parameters on this file or its versions. "
                    "However, the cache for file "
                    "transformations made using path "
                    "parameters will persist. You can purge "
                    "them using the purge API. For more "
                    "details, refer to the purge API "
                    "documentation.\n"
                    "\n"
                    "\n"
                    "\n"
                    "Default value - `false`\n",
                    "type": "boolean",
                },
            },
            "required": ["file_path", "new_file_name"],
            "type": "object",
        }
    },
)
async def rename_files_tool(
    file_path: str,
    new_file_name: str,
    purge_cache: Optional[bool] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Rename a file and all of its versions.

    Set purge_cache to purge CDN cache for old URLs (counts toward quota).

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await rename_files(
        file_path=file_path,
        new_file_name=new_file_name,
        purge_cache=purge_cache,
        filter_spec=filter_spec,
    )
