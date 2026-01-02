from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "folders",
    "operation": "write",
    "tags": [],
    "http_method": "post",
    "http_path": "/v1/bulkJobs/renameFolder",
    "operation_id": "rename-folder",
}


def _serialize_rename_job(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def rename_folders(
    *,
    folder_path: str,
    new_folder_name: str,
    purge_cache: Optional[bool] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Rename a folder and update paths for its nested assets.

    - Optionally purge cache for old URLs with purge_cache.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    body = {
        "folder_path": folder_path,
        "new_folder_name": new_folder_name,
        "purge_cache": purge_cache,
    }
    filtered_body = {k: v for k, v in body.items() if v is not None}

    raw = await CLIENT.folders.rename(**filtered_body)
    response = _serialize_rename_job(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="rename_folders",
    description="When using this tool, always use the `filter_spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nThis API allows you to rename an existing folder. The folder and all its nested assets and sub-folders will remain unchanged, but their paths will be updated to reflect the new folder name.\n\n\n# Response Schema\n```json\n{\n  type: 'object',\n  title: 'Async Bulk Job Response',\n  description: 'Job submitted successfully. A `jobId` will be returned.',\n  properties: {\n    jobId: {\n      type: 'string',\n      description: 'Unique identifier of the bulk job. This can be used to check the status of the bulk job.\\n'\n    }\n  },\n  required: [    'jobId'\n  ]\n}\n```",
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
                    "For more information, see the [glom"
                    "documentation](http://glom.readthedocs.io/).",
                    "title": "filter_spec",
                    "type": "string",
                },
                "folder_path": {
                    "description": "The full path to the folder you want to rename.\n",
                    "type": "string",
                },
                "new_folder_name": {
                    "description": "The new name for the folder.\n"
                    "\n"
                    "All characters except alphabets and "
                    "numbers (inclusive of unicode "
                    "letters, marks, and numerals in other "
                    "languages) and `-` will be replaced "
                    "by an underscore i.e. `_`.\n",
                    "type": "string",
                },
                "purge_cache": {
                    "description": "Option to purge cache for the old nested "
                    "files and their versions' URLs.\n"
                    "\n"
                    "When set to true, it will internally "
                    "issue a purge cache request on CDN to "
                    "remove the cached content of the old "
                    "nested files and their versions. There "
                    "will only be one purge request for all "
                    "the nested files, which will be counted "
                    "against your monthly purge quota.\n"
                    "\n"
                    "Note: A purge cache request will be "
                    "issued against "
                    "`https://ik.imagekit.io/old/folder/path*` "
                    "(with a wildcard at the end). This will "
                    "remove all nested files, their versions' "
                    "URLs, and any transformations made using "
                    "query parameters on these files or their "
                    "versions. However, the cache for file "
                    "transformations made using path "
                    "parameters will persist. You can purge "
                    "them using the purge API. For more "
                    "details, refer to the purge API "
                    "documentation.\n"
                    "\n"
                    "Default value - `false`\n",
                    "type": "boolean",
                },
            },
            "required": ["folder_path", "new_folder_name"],
            "type": "object",
        }
    },
)
async def rename_folders_tool(
    folder_path: str,
    new_folder_name: str,
    purge_cache: Optional[bool] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Rename a folder and update paths for its nested assets.

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await rename_folders(
        folder_path=folder_path,
        new_folder_name=new_folder_name,
        purge_cache=purge_cache,
        filter_spec=filter_spec,
    )
