from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "customMetadataFields",
    "operation": "write",
    "tags": [],
    "http_method": "delete",
    "http_path": "/v1/customMetadataFields/{id}",
    "operation_id": "delete-a-field",
}


def _serialize_delete_result(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def delete_custom_metadata_fields(
    *,
    id: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Delete a custom metadata field by ID.

    - Deleting a field is permanent; the name cannot be reused.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.custom_metadata_fields.delete(id)
    response = _serialize_delete_result(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="delete_custom_metadata_fields",
    description=(
        "Delete a custom metadata field from ImageKit by its unique identifier."
    ),
)
async def delete_custom_metadata_fields_tool(
    id: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Delete a custom metadata field.

    This tool deletes an existing custom metadata field using its unique
    identifier. The operation is idempotent—repeating the request for the
    same field ID has no additional effect.

    Once deleted, the metadata field name is permanently reserved and
    cannot be reused for creating a new custom metadata field.

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec` to select only the fields required from
    the response.

    Args:
        id: Unique identifier of the custom metadata field to delete.
        filter_spec: Optional glom-style filter specification used to
            reduce the response payload by selecting specific fields.
            Example: `.id`, `.name`

    Returns:
        An empty dictionary indicating the custom metadata field was
        successfully deleted.
    """
    return await delete_custom_metadata_fields(
        id=id,
        filter_spec=filter_spec,
    )
