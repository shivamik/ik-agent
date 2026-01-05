from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "customMetadataFields",
    "operation": "write",
    "tags": [],
    "http_method": "patch",
    "http_path": "/v1/customMetadataFields/{id}",
    "operation_id": "update-existing-field",
}


def _serialize_custom_metadata_field(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def update_custom_metadata_fields(
    *,
    id: str,
    label: Optional[str] = None,
    schema: Optional[Dict[str, Any]] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Update the label or schema of an existing custom metadata field.

    - Provide label, schema, or both; type is immutable and ignored if sent.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    body = {
        "label": label,
        "schema": schema,
    }
    filtered_body = {k: v for k, v in body.items() if v is not None}

    raw = await CLIENT.custom_metadata_fields.update(id, **filtered_body)
    response = _serialize_custom_metadata_field(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="update_custom_metadata_fields",
    description=("Update the label or schema of an existing custom metadata field."),
)
async def update_custom_metadata_fields_tool(
    id: str,
    label: Optional[str] = None,
    schema: Optional[Dict[str, Any]] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Update a custom metadata field definition.

    This tool updates an existing custom metadata field by modifying its
    human-readable label, its schema rules, or both.

    The metadata field `type` is immutable and cannot be changed after
    creation. If `type` is included inside `schema`, it will be ignored
    and validation will be performed against the existing field type.

    At least one of `label` or `schema` must be provided.

    To reduce response size and improve performance, it is recommended
    to use `filter_spec` to select only the required fields from the
    response.

    Args:
        id: Unique identifier of the custom metadata field to update.
        label: Optional new human-readable label for the field. Must be
            unique among non-deleted fields.
        schema: Optional schema updates defining validation rules such as
            default value, required flag, min/max constraints, or select
            options. The field type cannot be changed.
        filter_spec: Optional glom-style filter specification used to
            reduce the response payload.
            Example: `.id`, `.schema.type`

    Returns:
        The updated custom metadata field object, typically including:
            - id: Field identifier
            - label: Updated label
            - name: API name (unchanged)
            - schema: Updated schema definition
    """
    return await update_custom_metadata_fields(
        id=id,
        label=label,
        schema=schema,
        filter_spec=filter_spec,
    )
