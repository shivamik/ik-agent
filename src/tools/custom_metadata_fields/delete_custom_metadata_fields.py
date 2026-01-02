from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


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
    description="When using this tool, always use the `glom spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nThis API deletes a custom metadata field. Even after deleting a custom metadata field, you cannot create any new custom metadata field with the same name.\n\n\n# Response Schema\n```json\n{\n  type: 'object',\n  properties: {}\n}\n```",
    inputSchema={
        "json": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                },
                "filter_spec": {
                    "type": "string",
                    "title": "filter_spec",
                    "description": 'A filter_spec to apply to the response to include certain fields. Consult the output schema in the tool description to see the fields that are available.\n\nFor example: to include only the `name` field in every object of a results array, you can provide ".results[].name".\n\nFor more information, see the [glomdocumentation](http://glom.readthedocs.io/).',
                },
            },
            "required": ["id"],
        },
        "annotations": {
            "idempotentHint": "true",
        },
    },
)
async def delete_custom_metadata_fields_tool(
    id: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Delete a custom metadata field by ID.

    This operation is idempotent. Once deleted, the field name cannot be reused.

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await delete_custom_metadata_fields(
        id=id,
        filter_spec=filter_spec,
    )
