from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


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
)
async def create_folders_tool(
    folder_name: str,
    parent_folder_path: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Create a new folder in the ImageKit media library.

    This tool creates a folder with the given name under the specified
    parent folder path. If any part of the parent folder path does not
    already exist, it will be created automatically.

    Folder names are sanitized automatically: all characters except
    alphabets, numbers (including unicode characters), and hyphens (`-`)
    are replaced with underscores (`_`).

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec` to select only the fields required from
    the response.

    Args:
        folder_name: Name of the folder to be created.
        parent_folder_path: Path of the parent folder where the new
            folder should be created. Use `/` for the root folder.
            Example: `/product/images/`
        filter_spec: Optional glom-style filter specification used to
            reduce the response payload by selecting specific fields.
            Example: `.name`

    Returns:
        An empty dictionary, indicating the folder was created
        successfully.
    """
    return await create_folders(
        folder_name=folder_name,
        parent_folder_path=parent_folder_path,
        filter_spec=filter_spec,
    )
