from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "folders",
    "operation": "write",
    "tags": [],
    "http_method": "post",
    "http_path": "/v1/bulkJobs/copyFolder",
    "operation_id": "copy-folder",
}


def _serialize_copy_job(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def copy_folders(
    *,
    destination_path: str,
    source_folder_path: str,
    include_versions: Optional[bool] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Copy a folder and its contents to another folder.

    - Optionally include file versions with include_versions.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    body = {
        "destination_path": destination_path,
        "source_folder_path": source_folder_path,
        "include_versions": include_versions,
    }
    filtered_body = {k: v for k, v in body.items() if v is not None}

    raw = await CLIENT.folders.copy(**filtered_body)
    response = _serialize_copy_job(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="copy_folders",
    description="When using this tool, always use the `filter_spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nThis will copy one folder into another. The selected folder, its nested folders, files, and their versions (in `includeVersions` is set to true) are copied in this operation. Note: If any file at the destination has the same name as the source file, then the source file and its versions will be appended to the destination file version history.\n\n\n# Response Schema\n```json\n{\n  type: 'object',\n  title: 'Async Bulk Job Response',\n  description: 'Job submitted successfully. A `jobId` will be returned.',\n  properties: {\n    jobId: {\n      type: 'string',\n      description: 'Unique identifier of the bulk job. This can be used to check the status of the bulk job.\\n'\n    }\n  },\n  required: [    'jobId'\n  ]\n}\n```",
    inputSchema={
        "json": {
            "properties": {
                "destination_path": {
                    "description": "Full path to the destination folder "
                    "where you want to copy the source "
                    "folder into.\n",
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
                "include_versions": {
                    "description": "Option to copy all versions of files "
                    "that are nested inside the selected "
                    "folder. By default, only the current "
                    "version of each file will be copied. "
                    "When set to true, all versions of "
                    "each file will be copied. Default "
                    "value - `false`.\n",
                    "type": "boolean",
                },
                "source_folder_path": {
                    "description": "The full path to the source folder "
                    "you want to copy.\n",
                    "type": "string",
                },
            },
            "required": ["destination_path", "source_folder_path"],
            "type": "object",
        }
    },
)
async def copy_folders_tool(
    destination_path: str,
    source_folder_path: str,
    include_versions: Optional[bool] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Copy a folder and its contents to another folder.

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await copy_folders(
        destination_path=destination_path,
        source_folder_path=source_folder_path,
        include_versions=include_versions,
        filter_spec=filter_spec,
    )
