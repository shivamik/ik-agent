import logging
from strands import tool
from typing import Any, Dict, Optional, List

from src.clients import CLIENT
from src.config import LOG_LEVEL

logger = logging.getLogger("tools.files.update_files")
logger.setLevel(LOG_LEVEL)


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
    extensions: Optional[List[Dict[str, Any]]] = None,
    remove_ai_tags: Optional[Any] = None,
    tags: Optional[List[str]] = None,
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
    logger.info(f"Updating file {file_id} with body: {filtered_body}")
    return await CLIENT.files.update(file_id, **filtered_body)


@tool(
    name="update_files",
    description=(
        "Update metadata, tags, publication status, or apply extensions to an "
        "ImageKit file."
    ),
)
async def update_files_tool(
    file_id: str,
    custom_coordinates: Optional[str] = None,
    custom_metadata: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    extensions: Optional[List[Dict[str, Any]]] = None,
    remove_ai_tags: Optional[Any] = None,
    tags: Optional[List[str]] = None,
    webhook_url: Optional[str] = None,
    publish: Optional[Dict[str, Any]] = None,
) -> Any:
    """Update attributes of the current version of a file.

    This tool updates metadata and attributes of the current version of
    an ImageKit file. Supported updates include tags, ai tags, custom metadata,
    coordinates, description, AI tag removal, publication status, and
    applying AI or media processing extensions.

    Extensions such as background removal, auto-tagging, and auto-
    description can be applied as part of this operation.

    **Exclusivity rule**:
    The `publish` operation is mutually exclusive with all other update
    fields. If `publish` is provided, no other update parameters may be
    set.

    Args:
        file_id: Unique identifier of the file to update.
        custom_coordinates: Custom coordinates in `x,y,width,height` format.
        custom_metadata: Custom metadata key-value pairs to associate with
            the file.
        description: Human-readable description of the file contents.
        extensions: Optional list of dict of extensions to apply to the file,
            such as background removal, auto-tagging, or auto-description.
            ```[{"name": "remove-bg",
            "options": { "add_shadow": True } }, { "name": "google-auto-tagging",
            "minConfidence": 80,
            "maxTags": 10 }, { "name": "aws-auto-tagging",
            "minConfidence": 80,
            "maxTags": 10 }, { "name": "ai-auto-description" }]```
        remove_ai_tags: AI tags to remove, or `"all"` to remove all AI tags.
        tags: List of user-defined tags to assign to the file.
        webhook_url: Optional webhook URL to receive async extension updates.
        publish: Publication configuration. When provided, it must contain
            `is_published` and may optionally include
            `include_file_versions`.

    Raises:
        ValueError: If `publish` is provided together with other update fields.

    Returns:
        A response indicating the update was applied successfully. The
        response structure depends on the update operation performed.
    """

    # Enforce OpenAPI exclusivity: publish cannot be combined with other updates
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
