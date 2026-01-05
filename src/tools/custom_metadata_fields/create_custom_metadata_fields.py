from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "customMetadataFields",
    "operation": "write",
    "tags": [],
    "http_method": "post",
    "http_path": "/v1/customMetadataFields",
    "operation_id": "create-new-field",
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


async def create_custom_metadata_fields(
    *,
    label: str,
    name: str,
    schema: Dict[str, Any],
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Create a new custom metadata field.

    - Provide a unique label and API name plus a schema describing the field.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.custom_metadata_fields.create(
        label=label,
        name=name,
        schema=schema,
    )
    response = _serialize_custom_metadata_field(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="create_custom_metadata_fields",
    description=(
        "Create a new custom metadata field that can be assigned to ImageKit assets."
    ),
)
async def create_custom_metadata_fields_tool(
    label: str,
    name: str,
    schema: Dict[str, Any],
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Create a new custom metadata field.

    This tool defines a new custom metadata field that can later be
    populated on assets using the upload or update APIs. Once created,
    the field becomes available in both the Media Library UI and
    programmatic workflows.

    Custom metadata fields are strongly typed and validated based on
    the provided schema (e.g., text, number, date, select options).

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec` to select only the fields required from
    the response.

    Args:
        label: Human-readable name of the custom metadata field. This
            value is shown to users in the Media Library UI and must be
            unique among non-deleted custom metadata fields.
        name: API-safe name of the custom metadata field. This value is
            used as the key when setting `customMetadata` on assets and
            must be globally unique (including deleted fields).
        schema: Schema definition describing the type, validation rules,
            and constraints for the custom metadata field. At minimum,
            the schema must include a `type` value.
        filter_spec: Optional glom-style filter specification used to
            reduce the response payload by selecting specific fields.
            Example: `.id`, `.name`, `.schema.type`

    Returns:
        A dictionary containing details of the newly created custom
        metadata field, typically including:
            - id: Unique identifier of the custom metadata field.
            - label: Human-readable field label.
            - name: API name of the field.
            - schema: Validation and type rules for the field.
    """
    return await create_custom_metadata_fields(
        label=label,
        name=name,
        schema=schema,
        filter_spec=filter_spec,
    )
