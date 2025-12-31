from __future__ import annotations

from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "files",
    "operation": "write",
    "tags": [],
    "http_method": "post",
    "http_path": "/v1/files/copy",
    "operation_id": "copy-file",
}


def _serialize_copy_result(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def copy_files(
    *,
    destination_path: str,
    source_file_path: str,
    include_file_versions: Optional[bool] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Copy a file from one folder to another.

    - When destination has the same name, versions may be appended.
    - include_file_versions copies all versions when true.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    body = {
        "destination_path": destination_path,
        "source_file_path": source_file_path,
        "include_file_versions": include_file_versions,
    }
    filtered_body = {k: v for k, v in body.items() if v is not None}

    raw = await CLIENT.files.copy(**filtered_body)
    response = _serialize_copy_result(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="copy_files",
    description="When using this tool, always use the `filter_spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nThis will copy a file from one folder to another. \n\nNote: If any file at the destination has the same name as the source file, then the source file and its versions (if `includeFileVersions` is set to true) will be appended to the destination file version history.\n\n\n# Response Schema\n```json\n{\n  type: 'object',\n  properties: {}\n}\n```",
    inputSchema={
        "json": {
            "properties": {
                "destination_path": {
                    "description": "Full path to the folder you want to "
                    "copy the above file into.\n",
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
                "include_file_versions": {
                    "description": "Option to copy all versions of "
                    "a file. By default, only the "
                    "current version of the file is "
                    "copied. When set to true, all "
                    "versions of the file will be "
                    "copied. Default value - "
                    "`false`.\n",
                    "type": "boolean",
                },
                "source_file_path": {
                    "description": "The full path of the file you want to copy.\n",
                    "type": "string",
                },
            },
            "required": ["destination_path", "source_file_path"],
            "type": "object",
        }
    },
)
async def copy_files_tool(
    destination_path: str,
    source_file_path: str,
    include_file_versions: Optional[bool] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Copy a file from one folder to another.

    Set include_file_versions to copy all versions; otherwise only the
    current version is copied.

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await copy_files(
        destination_path=destination_path,
        source_file_path=source_file_path,
        include_file_versions=include_file_versions,
        filter_spec=filter_spec,
    )
