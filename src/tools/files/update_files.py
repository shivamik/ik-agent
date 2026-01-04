from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT


METADATA: Dict[str, Any] = {
    "resource": "files",
    "operation": "write",
    "tags": [],
    "http_method": "patch",
    "http_path": "/v1/files/{file_id}/details",
    "operation_id": "update-file-details",
}


async def update_files(
    *,
    file_id: str,
    custom_coordinates: Optional[str] = None,
    custom_metadata: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    extensions: Optional[Any] = None,
    remove_ai_tags: Optional[Any] = None,
    tags: Optional[Any] = None,
    webhook_url: Optional[str] = None,
    publish: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Update details of the current version of a file.

    Supports tags, custom coordinates/metadata, description, extensions,
    removing AI tags, webhook URL, and publish settings.
    """
    body = {
        "custom_coordinates": custom_coordinates,
        "custom_metadata": custom_metadata,
        "description": description,
        "extensions": extensions,
        "remove_ai_tags": remove_ai_tags,
        "tags": tags,
        "webhook_url": webhook_url,
        "publish": publish,
    }
    filtered_body = {k: v for k, v in body.items() if v is not None}

    return await CLIENT.files.update(file_id, **filtered_body)


@tool(
    name="update_files",
    description=(
        "This API updates the details or attributes of the current version of the file. "
        "You can update tags, customCoordinates, customMetadata, publication status, "
        "remove existing AITags and apply extensions using this API."
    ),
    inputSchema={
        "type": "object",
        "$defs": {
            "extensions": {
                "description": "Array of extensions to be applied to the asset.",
                "type": "array",
                "items": {
                    "anyOf": [
                        {
                            "type": "object",
                            "title": "Remove background",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "enum": ["remove-bg"],
                                },
                                "options": {
                                    "type": "object",
                                    "properties": {
                                        "add_shadow": {"type": "boolean"},
                                        "bg_color": {"type": "string"},
                                        "bg_image_url": {"type": "string"},
                                        "semitransparency": {"type": "boolean"},
                                    },
                                },
                            },
                            "required": ["name"],
                        },
                        {
                            "type": "object",
                            "title": "Auto tagging",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "enum": [
                                        "google-auto-tagging",
                                        "aws-auto-tagging",
                                    ],
                                },
                                "max_tags": {"type": "integer"},
                                "min_confidence": {"type": "integer"},
                            },
                            "required": ["name", "max_tags", "min_confidence"],
                        },
                        {
                            "type": "object",
                            "title": "Auto description",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "enum": ["ai-auto-description"],
                                }
                            },
                            "required": ["name"],
                        },
                    ]
                },
            }
        },
        "properties": {
            "file_id": {
                "type": "string",
                "description": "ID of the file to update",
            },
            # -------- metadata / extension updates --------
            "custom_coordinates": {
                "type": "string",
                "description": "x,y,width,height",
            },
            "custom_metadata": {
                "type": "object",
                "additionalProperties": True,
                "description": "Custom metadata key-value pairs",
            },
            "description": {
                "type": "string",
            },
            "extensions": {
                "$ref": "#/$defs/extensions",
            },
            "remove_ai_tags": {
                "description": "AITags to remove or 'all'",
                "anyOf": [
                    {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    {
                        "type": "string",
                        "enum": ["all"],
                    },
                ],
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
            },
            "webhook_url": {
                "type": "string",
            },
            # -------- publish block --------
            "publish": {
                "type": "object",
                "description": "Configure publication status",
                "properties": {
                    "include_file_versions": {
                        "type": "boolean",
                    },
                    "is_published": {
                        "type": "boolean",
                    },
                },
                "required": ["is_published"],
            },
        },
        "required": ["file_id"],
    },
)
async def update_files_tool(
    file_id: str,
    custom_coordinates: Optional[str] = None,
    custom_metadata: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    extensions: Optional[Any] = None,
    remove_ai_tags: Optional[Any] = None,
    tags: Optional[Any] = None,
    webhook_url: Optional[str] = None,
    publish: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Update details of the current version of a file.
    """

    # Optional: enforce original OpenAPI exclusivity
    if publish is not None:
        if any(
            v is not None
            for v in [
                custom_coordinates,
                custom_metadata,
                description,
                extensions,
                remove_ai_tags,
                tags,
            ]
        ):
            raise ValueError("publish cannot be combined with other update fields")

    return await update_files(
        file_id=file_id,
        custom_coordinates=custom_coordinates,
        custom_metadata=custom_metadata,
        description=description,
        extensions=extensions,
        remove_ai_tags=remove_ai_tags,
        tags=tags,
        webhook_url=webhook_url,
        publish=publish,
    )
