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
    description="This API updates the details or attributes of the current version of the file. You can update `tags`, `customCoordinates`, `customMetadata`, publication status, remove existing `AITags` and apply extensions using this API.\n",
    inputSchema={
        "json": {
            "$defs": {
                "extensions": {
                    "description": "Array of extensions to be applied to the asset. "
                    "Each extension can be configured with specific "
                    "parameters based on the extension type.\n",
                    "items": {
                        "anyOf": [
                            {
                                "properties": {
                                    "name": {
                                        "description": "Specifies "
                                        "the "
                                        "background "
                                        "removal "
                                        "extension.",
                                        "enum": ["remove-bg"],
                                        "type": "string",
                                    },
                                    "options": {
                                        "properties": {
                                            "add_shadow": {
                                                "description": "Whether "
                                                "to "
                                                "add "
                                                "an "
                                                "artificial "
                                                "shadow "
                                                "to "
                                                "the "
                                                "result. "
                                                "Default "
                                                "is "
                                                "false. "
                                                "Note: "
                                                "Adding "
                                                "shadows "
                                                "is "
                                                "currently "
                                                "only "
                                                "supported "
                                                "for "
                                                "car "
                                                "photos.\n",
                                                "type": "boolean",
                                            },
                                            "bg_color": {
                                                "description": "Specifies "
                                                "a "
                                                "solid "
                                                "color "
                                                "background "
                                                "using "
                                                "hex "
                                                "code "
                                                "(e.g., "
                                                '"81d4fa", '
                                                '"fff") '
                                                "or "
                                                "color "
                                                "name "
                                                "(e.g., "
                                                '"green"). '
                                                "If "
                                                "this "
                                                "parameter "
                                                "is "
                                                "set, "
                                                "`bg_image_url` "
                                                "must "
                                                "be "
                                                "empty.\n",
                                                "type": "string",
                                            },
                                            "bg_image_url": {
                                                "description": "Sets "
                                                "a "
                                                "background "
                                                "image "
                                                "from "
                                                "a "
                                                "URL. "
                                                "If "
                                                "this "
                                                "parameter "
                                                "is "
                                                "set, "
                                                "`bg_color` "
                                                "must "
                                                "be "
                                                "empty.\n",
                                                "type": "string",
                                            },
                                            "semitransparency": {
                                                "description": "Allows "
                                                "semi-transparent "
                                                "regions "
                                                "in "
                                                "the "
                                                "result. "
                                                "Default "
                                                "is "
                                                "true. "
                                                "Note: "
                                                "Semitransparency "
                                                "is "
                                                "currently "
                                                "only "
                                                "supported "
                                                "for "
                                                "car "
                                                "windows.\n",
                                                "type": "boolean",
                                            },
                                        },
                                        "type": "object",
                                    },
                                },
                                "required": ["name"],
                                "title": "Remove background",
                                "type": "object",
                            },
                            {
                                "properties": {
                                    "max_tags": {
                                        "description": "Maximum "
                                        "number "
                                        "of "
                                        "tags "
                                        "to "
                                        "attach "
                                        "to "
                                        "the "
                                        "asset.",
                                        "type": "integer",
                                    },
                                    "min_confidence": {
                                        "description": "Minimum "
                                        "confidence "
                                        "level "
                                        "for "
                                        "tags "
                                        "to "
                                        "be "
                                        "considered "
                                        "valid.",
                                        "type": "integer",
                                    },
                                    "name": {
                                        "description": "Specifies "
                                        "the "
                                        "auto-tagging "
                                        "extension "
                                        "used.",
                                        "enum": [
                                            "google-auto-tagging",
                                            "aws-auto-tagging",
                                        ],
                                        "type": "string",
                                    },
                                },
                                "required": ["max_tags", "min_confidence", "name"],
                                "title": "Auto tagging",
                                "type": "object",
                            },
                            {
                                "properties": {
                                    "name": {
                                        "description": "Specifies "
                                        "the "
                                        "auto "
                                        "description "
                                        "extension.",
                                        "enum": ["ai-auto-description"],
                                        "type": "string",
                                    }
                                },
                                "required": ["name"],
                                "title": "Auto description",
                                "type": "object",
                            },
                        ]
                    },
                    "title": "Extensions Array",
                    "type": "array",
                }
            },
            "anyOf": [
                {
                    "properties": {
                        "custom_coordinates": {
                            "description": "Define an important "
                            "area in the image in "
                            "the format "
                            "`x,y,width,height` e.g. "
                            "`10,10,100,100`. Send "
                            "`null` to unset this "
                            "value.\n",
                            "type": "string",
                        },
                        "custom_metadata": {
                            "additionalProperties": "true",
                            "description": "A key-value data to be "
                            "associated with the asset. "
                            "To unset a key, send "
                            "`null` value for that key. "
                            "Before setting any custom "
                            "metadata on an asset you "
                            "have to create the field "
                            "using custom metadata "
                            "fields API.\n",
                            "type": "object",
                        },
                        "description": {
                            "description": "Optional text to describe the "
                            "contents of the file.\n",
                            "type": "string",
                        },
                        "extensions": {"$ref": "#/$defs/extensions"},
                        "file_id": {"type": "string"},
                        "remove_ai_tags": {
                            "anyOf": [
                                {"items": {"type": "string"}, "type": "array"},
                                {"enum": ["all"], "type": "string"},
                            ],
                            "description": "An array of AITags "
                            "associated with the file "
                            "that you want to remove, "
                            'e.g. `["car", "vehicle", '
                            '"motorsports"]`. \n'
                            "\n"
                            "If you want to remove all "
                            "AITags associated with the "
                            "file, send a string - "
                            '"all".\n'
                            "\n"
                            "Note: The remove operation "
                            "for `AITags` executes "
                            "before any of the "
                            "`extensions` are "
                            "processed.\n",
                        },
                        "tags": {
                            "description": "An array of tags associated with the "
                            'file, such as `["tag1", "tag2"]`. '
                            "Send `null` to unset all tags "
                            "associated with the file.\n",
                            "items": {"type": "string"},
                            "type": "array",
                        },
                        "webhook_url": {
                            "description": "The final status of extensions "
                            "after they have completed "
                            "execution will be delivered to "
                            "this endpoint as a POST "
                            "request. [Learn "
                            "more](/docs/api-reference/digital-asset-management-dam/managing-assets/update-file-details#webhook-payload-structure) "
                            "about the webhook payload "
                            "structure.\n",
                            "type": "string",
                        },
                    },
                    "required": ["file_id"],
                    "type": "object",
                },
                {
                    "properties": {
                        "file_id": {"type": "string"},
                        "publish": {
                            "description": "Configure the publication status "
                            "of a file and its versions.\n",
                            "properties": {
                                "include_file_versions": {
                                    "description": "Set "
                                    "to "
                                    "`true` "
                                    "to "
                                    "publish/unpublish "
                                    "all "
                                    "versions "
                                    "of "
                                    "the "
                                    "file. "
                                    "Set "
                                    "to "
                                    "`false` "
                                    "to "
                                    "publish/unpublish "
                                    "only "
                                    "the "
                                    "current "
                                    "version "
                                    "of "
                                    "the "
                                    "file.\n",
                                    "type": "boolean",
                                },
                                "is_published": {
                                    "description": "Set "
                                    "to "
                                    "`true` "
                                    "to "
                                    "publish "
                                    "the "
                                    "file. "
                                    "Set "
                                    "to "
                                    "`false` "
                                    "to "
                                    "unpublish "
                                    "the "
                                    "file.\n",
                                    "type": "boolean",
                                },
                            },
                            "required": ["is_published"],
                            "type": "object",
                        },
                    },
                    "required": ["file_id"],
                    "type": "object",
                },
            ],
            "type": "object",
        }
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
