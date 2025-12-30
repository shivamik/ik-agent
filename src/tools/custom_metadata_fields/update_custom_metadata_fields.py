from __future__ import annotations

from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


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
    description="When using this tool, always use the `filter_spec` parameter to reduce the response size and improve performance.\n\nOnly omit if you're sure you don't need the data.\n\nThis API updates the label or schema of an existing custom metadata field.\n\n\n# Response Schema\n```json\n{\n  $ref: '#/$defs/custom_metadata_field',\n  $defs: {\n    custom_metadata_field: {\n      type: 'object',\n      description: 'Object containing details of a custom metadata field.',\n      properties: {\n        id: {\n          type: 'string',\n          description: 'Unique identifier for the custom metadata field. Use this to update the field.'\n        },\n        label: {\n          type: 'string',\n          description: 'Human readable name of the custom metadata field. This name is displayed as form field label to the users while setting field value on the asset in the media library UI.\\n'\n        },\n        name: {\n          type: 'string',\n          description: 'API name of the custom metadata field. This becomes the key while setting `customMetadata` (key-value object) for an asset using upload or update API.\\n'\n        },\n        schema: {\n          type: 'object',\n          description: 'An object that describes the rules for the custom metadata field value.',\n          properties: {\n            type: {\n              type: 'string',\n              description: 'Type of the custom metadata field.',\n              enum: [                'Text',\n                'Textarea',\n                'Number',\n                'Date',\n                'Boolean',\n                'SingleSelect',\n                'MultiSelect'\n              ]\n            },\n            defaultValue: {\n              anyOf: [                {\n                  type: 'string'\n                },\n                {\n                  type: 'number'\n                },\n                {\n                  type: 'boolean'\n                },\n                {\n                  type: 'array',\n                  title: 'Mixed',\n                  description: 'Default value should be of type array when custom metadata field type is set to `MultiSelect`.\\n',\n                  items: {\n                    anyOf: [                      {\n                        type: 'string'\n                      },\n                      {\n                        type: 'number'\n                      },\n                      {\n                        type: 'boolean'\n                      }\n                    ]\n                  }\n                }\n              ],\n              description: 'The default value for this custom metadata field. Data type of default value depends on the field type.\\n'\n            },\n            isValueRequired: {\n              type: 'boolean',\n              description: 'Specifies if the this custom metadata field is required or not.\\n'\n            },\n            maxLength: {\n              type: 'number',\n              description: 'Maximum length of string. Only set if `type` is set to `Text` or `Textarea`.\\n'\n            },\n            maxValue: {\n              anyOf: [                {\n                  type: 'string'\n                },\n                {\n                  type: 'number'\n                }\n              ],\n              description: 'Maximum value of the field. Only set if field type is `Date` or `Number`. For `Date` type field, the value will be in ISO8601 string format. For `Number` type field, it will be a numeric value.\\n'\n            },\n            minLength: {\n              type: 'number',\n              description: 'Minimum length of string. Only set if `type` is set to `Text` or `Textarea`.\\n'\n            },\n            minValue: {\n              anyOf: [                {\n                  type: 'string'\n                },\n                {\n                  type: 'number'\n                }\n              ],\n              description: 'Minimum value of the field. Only set if field type is `Date` or `Number`. For `Date` type field, the value will be in ISO8601 string format. For `Number` type field, it will be a numeric value.\\n'\n            },\n            selectOptions: {\n              type: 'array',\n              description: 'An array of allowed values when field type is `SingleSelect` or `MultiSelect`.\\n',\n              items: {\n                anyOf: [                  {\n                    type: 'string'\n                  },\n                  {\n                    type: 'number'\n                  },\n                  {\n                    type: 'boolean'\n                  }\n                ]\n              }\n            }\n          },\n          required: [            'type'\n          ]\n        }\n      },\n      required: [        'id',\n        'label',\n        'name',\n        'schema'\n      ]\n    }\n  }\n}\n```",
    inputSchema={
        "json": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                },
                "label": {
                    "type": "string",
                    "description": "Human readable name of the custom metadata field. This should be unique across all non deleted custom metadata fields. This name is displayed as form field label to the users while setting field value on an asset in the media library UI. This parameter is required if `schema` is not provided.",
                },
                "schema": {
                    "type": "object",
                    "description": "An object that describes the rules for the custom metadata key. This parameter is required if `label` is not provided. Note: `type` cannot be updated and will be ignored if sent with the `schema`. The schema will be validated as per the existing `type`.\n",
                    "properties": {
                        "defaultValue": {
                            "anyOf": [
                                {
                                    "type": "string",
                                },
                                {
                                    "type": "number",
                                },
                                {
                                    "type": "boolean",
                                },
                                {
                                    "type": "array",
                                    "title": "Mixed",
                                    "description": "Default value should be of type array when custom metadata field type is set to `MultiSelect`.\n",
                                    "items": {
                                        "anyOf": [
                                            {
                                                "type": "string",
                                            },
                                            {
                                                "type": "number",
                                            },
                                            {
                                                "type": "boolean",
                                            },
                                        ],
                                    },
                                },
                            ],
                            "description": "The default value for this custom metadata field. This property is only required if `isValueRequired` property is set to `true`. The value should match the `type` of custom metadata field.\n",
                        },
                        "isValueRequired": {
                            "type": "boolean",
                            "description": "Sets this custom metadata field as required. Setting custom metadata fields on an asset will throw error if the value for all required fields are not present in upload or update asset API request body.\n",
                        },
                        "maxLength": {
                            "type": "number",
                            "description": "Maximum length of string. Only set this property if `type` is set to `Text` or `Textarea`.\n",
                        },
                        "maxValue": {
                            "anyOf": [
                                {
                                    "type": "string",
                                },
                                {
                                    "type": "number",
                                },
                            ],
                            "description": "Maximum value of the field. Only set this property if field type is `Date` or `Number`. For `Date` type field, set the minimum date in ISO8601 string format. For `Number` type field, set the minimum numeric value.\n",
                        },
                        "minLength": {
                            "type": "number",
                            "description": "Minimum length of string. Only set this property if `type` is set to `Text` or `Textarea`.\n",
                        },
                        "minValue": {
                            "anyOf": [
                                {
                                    "type": "string",
                                },
                                {
                                    "type": "number",
                                },
                            ],
                            "description": "Minimum value of the field. Only set this property if field type is `Date` or `Number`. For `Date` type field, set the minimum date in ISO8601 string format. For `Number` type field, set the minimum numeric value.\n",
                        },
                        "selectOptions": {
                            "type": "array",
                            "description": "An array of allowed values. This property is only required if `type` property is set to `SingleSelect` or `MultiSelect`.\n",
                            "items": {
                                "anyOf": [
                                    {
                                        "type": "string",
                                    },
                                    {
                                        "type": "number",
                                    },
                                    {
                                        "type": "boolean",
                                    },
                                ],
                            },
                        },
                    },
                },
                "filter_spec": {
                    "type": "string",
                    "title": "filter_spec",
                    "description": 'A filter_spec to apply to the response to include certain fields. Consult the output schema in the tool description to see the fields that are available.\n\nFor example: to include only the `name` field in every object of a results array, you can provide ".results[].name".\n\nFor more information, see the [jq documentation](https://jqlang.org/manual/).',
                },
            },
            "required": ["id"],
        }
    },
)
async def update_custom_metadata_fields_tool(
    id: str,
    label: Optional[str] = None,
    schema: Optional[Dict[str, Any]] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Update the label or schema of an existing custom metadata field.

    Provide label, schema, or both. The field `type` cannot be updated.

    To reduce response size and improve performance, prefer using
    `filter_spec` to select only the fields you need.
    """
    return await update_custom_metadata_fields(
        id=id,
        label=label,
        schema=schema,
        filter_spec=filter_spec,
    )
