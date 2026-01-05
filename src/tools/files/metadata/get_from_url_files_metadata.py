from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "files.metadata",
    "operation": "read",
    "tags": [],
    "http_method": "get",
    "http_path": "/v1/files/metadata",
    "operation_id": "get-metadata-from-url",
}


def _serialize_metadata(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def get_from_url_files_metadata(
    *,
    url: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Retrieve metadata (EXIF, pHash, etc.) for an accessible URL.

    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    raw = await CLIENT.files.metadata.get_from_url(
        url=url,
    )
    response = _serialize_metadata(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="get_from_url_files_metadata",
    description=(
        "Retrieve technical metadata for a remotely hosted file URL using ImageKit."
    ),
)
async def get_from_url_files_metadata_tool(
    url: str,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Retrieve metadata for a file accessible via URL.

    This tool fetches technical metadata for a file hosted at a remote
    URL using ImageKit’s metadata extraction pipeline. Depending on the
    file type, the response may include EXIF information, perceptual
    hash (pHash), dimensions, color profile details, and audio/video
    codec attributes.

    The provided URL must be accessible using the configured ImageKit
    account and reachable by ImageKit’s servers.

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec` to select only the fields required from
    the response.

    Args:
        url: Publicly accessible URL of the file for which metadata
            should be retrieved.
        filter_spec: Optional glom-style filter specification used to
            reduce the response payload by selecting specific fields.
            Example: `.exif`, `.pHash`, `.width`, `.height`

    Returns:
        A dictionary containing extracted metadata for the remote file,
        which may include:
            - exif: Camera and image metadata (if available).
            - pHash: Perceptual hash for similarity comparison.
            - width / height: Dimensions of the file.
            - size: File size in bytes.
            - format: File format (e.g., `jpg`, `png`, `mp4`).
            - audioCodec / videoCodec: Codec information for media files.
            - duration / bitRate: Media-specific properties (videos/audio).
    """
    return await get_from_url_files_metadata(
        url=url,
        filter_spec=filter_spec,
    )
