from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


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
)
async def rename_folders_tool(
    folder_path: str,
    new_folder_name: str,
    purge_cache: Optional[bool] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Rename an ImageKit folder and update paths for all nested assets.

    This tool renames an existing folder while preserving its contents.
    All nested files and sub-folders remain unchanged, but their paths
    are updated to reflect the new folder name. The operation is executed
    asynchronously as a bulk job.

    To reduce response size and improve performance, it is strongly
    recommended to provide a `filter_spec` to select only the fields
    required from the response.

    Args:
        folder_path: The full path of the folder to be renamed.
        new_folder_name: The new name for the folder.
            All characters except alphabets, numbers (including unicode),
            and hyphens (`-`) are replaced with underscores (`_`).
        purge_cache: Whether to purge CDN cache for all old nested file URLs.
            If set to `True`, a single wildcard purge request will be issued
            for the old folder path and counted against the monthly purge quota.
            Defaults to `False`.
        filter_spec: Optional glom-style filter specification used to reduce
            the response payload by selecting specific fields.
            Example: `.jobId`

    Returns:
        A dictionary containing the submitted bulk job details, typically:
            - jobId: Unique identifier for the asynchronous bulk job, which
              can be used to query job status.
    """
    return await rename_folders(
        folder_path=folder_path,
        new_folder_name=new_folder_name,
        purge_cache=purge_cache,
        filter_spec=filter_spec,
    )
