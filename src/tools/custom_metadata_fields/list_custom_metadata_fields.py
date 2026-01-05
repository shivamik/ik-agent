from typing import Any, Dict, List, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "customMetadataFields",
    "operation": "read",
    "tags": [],
    "http_method": "get",
    "http_path": "/v1/customMetadataFields",
    "operation_id": "list-all-fields",
}


def _serialize_custom_metadata_field(field: Any) -> Dict[str, Any]:
    """
    Normalize SDK custom metadata field objects into plain dicts.
    """
    if hasattr(field, "model_dump"):
        return field.model_dump()
    if hasattr(field, "dict"):
        return field.dict()
    return dict(field)


async def list_custom_metadata_fields(
    *,
    folder_path: Optional[str] = None,
    include_deleted: Optional[bool] = None,
    filter_spec: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """
    List custom metadata fields.

    - By default returns non-deleted fields; use include_deleted to include deleted.
    - Use folder_path to filter fields applicable to a specific path policy.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    body = {
        "folder_path": folder_path,
        "include_deleted": include_deleted,
    }

    filtered_body = {k: v for k, v in body.items() if v is not None}

    raw_fields = await CLIENT.custom_metadata_fields.list(**filtered_body)
    response = [_serialize_custom_metadata_field(field) for field in raw_fields]

    return maybe_filter(filter_spec, response)


@tool(
    name="list_custom_metadata_fields",
    description=(
        "List custom metadata fields defined in ImageKit, with optional "
        "filters for deletion status and folder path."
    ),
)
async def list_custom_metadata_fields_tool(
    folder_path: Optional[str] = None,
    include_deleted: Optional[bool] = None,
    filter_spec: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """List custom metadata fields.

    This tool returns the collection of custom metadata field definitions
    created in ImageKit. By default, only non-deleted fields are returned.
    Deleted fields can be included by setting `include_deleted` to True.

    When the Path Policy feature is enabled, this tool can also filter
    metadata fields applicable to a specific folder path. This is useful
    for determining which metadata fields are available or enforced at a
    given location in the media library.

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec` to select only the fields required from
    the response.

    Args:
        folder_path: Optional folder path (e.g. `/images/products/`) used
            to retrieve custom metadata fields applicable to that path.
            Relevant when Path Policy is enabled.
        include_deleted: Whether to include deleted custom metadata fields
            in the response. Defaults to False.
        filter_spec: Optional glom-style filter specification used to
            reduce the response payload by selecting specific fields.
            Example: `.name`, `.schema.type`

    Returns:
        A list of custom metadata field objects. Each field typically
        includes:
            - id: Unique identifier of the custom metadata field.
            - label: Human-readable field label.
            - name: API name of the field.
            - schema: Validation and type rules for the field.
    """
    return await list_custom_metadata_fields(
        folder_path=folder_path,
        include_deleted=include_deleted,
        filter_spec=filter_spec,
    )
