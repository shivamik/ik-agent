from pathlib import Path
from typing import Any, Dict, Optional, Sequence
from urllib.parse import urlparse

from strands import tool

from src.config import TEMP_DIR
from src.clients import CLIENT
from src.utils.file_utils import resolve_image_input
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "files",
    "operation": "write",
    "tags": [],
    "http_method": "post",
    "http_path": "/api/v1/files/upload",
    "operation_id": "upload-file",
}


def _serialize_upload_result(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def upload_files(
    *,
    file: Any,
    file_name: str,
    token: Optional[str] = None,
    checks: Optional[str] = None,
    custom_coordinates: Optional[str] = None,
    custom_metadata: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    expire: Optional[int] = None,
    extensions: Optional[Any] = None,
    folder: Optional[str] = None,
    is_private_file: Optional[bool] = None,
    is_published: Optional[bool] = None,
    overwrite_ai_tags: Optional[bool] = None,
    overwrite_custom_metadata: Optional[bool] = None,
    overwrite_file: Optional[bool] = None,
    overwrite_tags: Optional[bool] = None,
    public_key: Optional[str] = None,
    response_fields: Optional[Sequence[str]] = None,
    signature: Optional[str] = None,
    tags: Optional[Sequence[str]] = None,
    transformation: Optional[Any] = None,
    use_unique_file_name: Optional[bool] = None,
    webhook_url: Optional[str] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Upload a file to ImageKit (V1 upload API).

    - Supports binary data, URL, or Base64 with required file_name.
    - Optional client-side auth fields: token, signature, expire, public_key.
    - Optional overwrite, privacy, tags, metadata, transformations, extensions.
    - Use `filter_spec` (glom spec) to shrink the response payload.
    """
    if isinstance(file, str):
        parsed = urlparse(file)
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            resolved = resolve_image_input(file, output_dir=TEMP_DIR)
            file = resolved

    body = {
        "file": file,
        "file_name": file_name,
        "token": token,
        "checks": checks,
        "custom_coordinates": custom_coordinates,
        "custom_metadata": custom_metadata,
        "description": description,
        "expire": expire,
        "extensions": extensions,
        "folder": folder,
        "is_private_file": is_private_file,
        "is_published": is_published,
        "overwrite_ai_tags": overwrite_ai_tags,
        "overwrite_custom_metadata": overwrite_custom_metadata,
        "overwrite_file": overwrite_file,
        "overwrite_tags": overwrite_tags,
        "public_key": public_key,
        "response_fields": response_fields,
        "signature": signature,
        "tags": tags,
        "transformation": transformation,
        "use_unique_file_name": use_unique_file_name,
        "webhook_url": webhook_url,
    }

    filtered_body = {k: v for k, v in body.items() if v is not None}

    raw = await CLIENT.files.upload(**filtered_body)
    response = _serialize_upload_result(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="upload_files",
    description=(
        "Upload a file to ImageKit with optional metadata, transformations, "
        "extensions, and client-side authentication support."
    ),
)
async def upload_files_tool(
    file: Any,
    file_name: str,
    token: Optional[str] = None,
    checks: Optional[str] = None,
    custom_coordinates: Optional[str] = None,
    custom_metadata: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    expire: Optional[int] = None,
    extensions: Optional[Any] = None,
    folder: Optional[str] = None,
    is_private_file: Optional[bool] = None,
    is_published: Optional[bool] = None,
    overwrite_ai_tags: Optional[bool] = None,
    overwrite_custom_metadata: Optional[bool] = None,
    overwrite_file: Optional[bool] = None,
    overwrite_tags: Optional[bool] = None,
    public_key: Optional[str] = None,
    response_fields: Optional[Sequence[str]] = None,
    signature: Optional[str] = None,
    tags: Optional[Sequence[str]] = None,
    transformation: Optional[Any] = None,
    use_unique_file_name: Optional[bool] = None,
    webhook_url: Optional[str] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Upload a file to ImageKit.

    This tool uploads a file to the ImageKit media library using the V1
    upload API. Files can be uploaded from the server or client side.

    Supported file inputs include:
    - Raw binary data (multipart form upload)
    - Publicly accessible HTTP/HTTPS URLs
    - Base64-encoded strings or data URIs

    Client-side uploads require `token`, `signature`, and `expire`
    parameters generated securely using the private API key.

    During upload, you can configure metadata, tags, transformations,
    extensions, access control, overwrite behavior, and webhook callbacks.

    To reduce response size and improve performance, it is recommended
    to provide a `filter_spec` to select only the fields required from
    the response.

    Args:
        file: File content to upload. Can be binary data, a public URL,
            or a Base64-encoded string.
        file_name: Name with which the file will be stored. Unsupported
            characters are replaced with underscores (`_`).
        token: Client-side upload token (required for browser uploads).
        signature: HMAC signature generated using the private API key
            (required for client-side uploads).
        expire: Unix timestamp (in seconds) indicating token expiry.
        public_key: ImageKit public key (required for client-side uploads).
        folder: Destination folder path. Nested folders are created
            automatically if they do not exist.
        checks: Optional server-side upload checks.
        custom_coordinates: Area of interest in `x,y,width,height` format.
        custom_metadata: Custom metadata key-value pairs for the asset.
        description: Human-readable description of the file.
        tags: Tags to associate with the file.
        extensions: Extensions to apply during upload, such as background
            removal, auto-tagging, or auto-description.
        transformation: Pre- or post-processing transformations to apply.
        is_private_file: Whether the file should be private.
        is_published: Whether the file should be published immediately.
        overwrite_file: Whether to overwrite an existing file at the same
            path when `use_unique_file_name` is `False`.
        overwrite_tags: Whether to overwrite existing tags on overwrite.
        overwrite_ai_tags: Whether to overwrite AI-generated tags.
        overwrite_custom_metadata: Whether to overwrite custom metadata.
        use_unique_file_name: Whether to append a unique suffix to the file
            name to avoid collisions.
        response_fields: List of response fields to include in the API
            response body.
        webhook_url: Webhook endpoint to receive async extension results.
        filter_spec: Optional glom-style filter specification used to
            reduce the response payload.

    Returns:
        A dictionary containing details of the uploaded file, including
        file identifiers, URLs, metadata, and any requested response fields.
    """
    return await upload_files(
        file=file,
        file_name=file_name,
        token=token,
        checks=checks,
        custom_coordinates=custom_coordinates,
        custom_metadata=custom_metadata,
        description=description,
        expire=expire,
        extensions=extensions,
        folder=folder,
        is_private_file=is_private_file,
        is_published=is_published,
        overwrite_ai_tags=overwrite_ai_tags,
        overwrite_custom_metadata=overwrite_custom_metadata,
        overwrite_file=overwrite_file,
        overwrite_tags=overwrite_tags,
        public_key=public_key,
        response_fields=response_fields,
        signature=signature,
        tags=tags,
        transformation=transformation,
        use_unique_file_name=use_unique_file_name,
        webhook_url=webhook_url,
        filter_spec=filter_spec,
    )
