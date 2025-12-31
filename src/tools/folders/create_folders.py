from __future__ import annotations

from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "folders",
    "operation": "write",
    "tags": [],
    "http_method": "post",
    "http_path": "/v1/folder",
    "operation_id": "create-folder",
}


def _serialize_create_folder_result(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def create_folders(
    *,
    folder_name: str,
    parent_folder_path: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Create a new folder in the media library.

    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.folders.create(
        folder_name=folder_name,
        parent_folder_path=parent_folder_path,
    )
    response = _serialize_create_folder_result(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="create_folders",
    description="When using this tool, always use the `filter_spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nThis will create a new folder. You can specify the folder name and location of the parent folder where this new folder should be created.\n\n\n# Response Schema\n```json\n{\n  type: 'object',\n  properties: {}\n}\n```",
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
                "folder_name": {
                    "description": "The folder will be created with this "
                    "name. \n"
                    "\n"
                    "All characters except alphabets and "
                    "numbers (inclusive of unicode letters, "
                    "marks, and numerals in other languages) "
                    "will be replaced by an underscore i.e. "
                    "`_`.\n",
                    "type": "string",
                },
                "parent_folder_path": {
                    "description": "The folder where the new folder "
                    "should be created, for root use "
                    "`/` else the path e.g. "
                    "`containing/folder/`.\n"
                    "\n"
                    "Note: If any folder(s) is not "
                    "present in the parentFolderPath "
                    "parameter, it will be "
                    "automatically created. For "
                    "example, if you pass "
                    "`/product/images/summer`, then "
                    "`product`, `images`, and `summer` "
                    "folders will be created if they "
                    "don't already exist.\n",
                    "type": "string",
                },
            },
            "required": ["folder_name", "parent_folder_path"],
            "type": "object",
        }
    },
)
async def create_folders_tool(
    folder_name: str,
    parent_folder_path: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Create a new folder in the media library.

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await create_folders(
        folder_name=folder_name,
        parent_folder_path=parent_folder_path,
        filter_spec=filter_spec,
    )
