from typing import Any, Dict, Optional, Sequence

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


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
    description=("Add tags to multiple ImageKit files in a single bulk operation."),
)
async def add_tags_files_bulk_tool(
    file_ids: Sequence[str],
    tags: Sequence[str],
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Add tags to multiple files in bulk.

    This tool adds one or more tags to multiple files in a single request.
    A maximum of 50 file IDs can be processed per call.

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec` to select only the fields required from
    the response.

    Args:
        file_ids: Sequence of file IDs to which tags should be added.
            Maximum allowed is 50 file IDs per request.
        tags: Sequence of tags to add to the specified files.
        filter_spec: Optional glom-style filter specification used to
            reduce the response payload by selecting specific fields.
            Example: `.successfullyUpdatedFileIds`

    Returns:
        A dictionary containing the bulk operation result, typically:
            - successfullyUpdatedFileIds: List of file IDs for which
              tags were successfully added.
    """
    return await add_tags_files_bulk(
        file_ids=file_ids,
        tags=tags,
        filter_spec=filter_spec,
    )
