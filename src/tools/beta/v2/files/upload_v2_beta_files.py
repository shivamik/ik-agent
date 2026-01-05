from typing import Any, Dict, Optional, Sequence

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter
from urllib.parse import urlparse
from src.utils.file_utils import resolve_image_input
from src.config import TEMP_DIR

METADATA: Dict[str, Any] = {
    "resource": "beta.v2.files",
    "operation": "write",
    "tags": [],
    "http_method": "post",
    "http_path": "/api/v2/files/upload",
    "operation_id": "upload-file-v2",
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


async def upload_v2_beta_files(
    *,
    file: Any,
    file_name: str,
    token: Optional[str] = None,
    checks: Optional[str] = None,
    custom_coordinates: Optional[str] = None,
    custom_metadata: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    extensions: Optional[Any] = None,
    folder: Optional[str] = None,
    is_private_file: Optional[bool] = None,
    is_published: Optional[bool] = None,
    overwrite_ai_tags: Optional[bool] = None,
    overwrite_custom_metadata: Optional[bool] = None,
    overwrite_file: Optional[bool] = None,
    overwrite_tags: Optional[bool] = None,
    response_fields: Optional[Sequence[str]] = None,
    tags: Optional[Sequence[str]] = None,
    transformation: Optional[Any] = None,
    use_unique_file_name: Optional[bool] = None,
    webhook_url: Optional[str] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Upload a file using the ImageKit V2 beta upload API (JWT-verified payload).

    - Supports binary data, URL, or Base64 (file field required) with `file_name`.
    - Optional JWT `token` for client-side uploads; must be generated server-side.
    - Optional flags to control overwrites, privacy, publishing, tags, and metadata.
    - `transformation` and `extensions` let you run pre/post processing or extensions.
    - Use `filter_spec` (glom spec) to project the response.
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
        "extensions": extensions,
        "folder": folder,
        "is_private_file": is_private_file,
        "is_published": is_published,
        "overwrite_ai_tags": overwrite_ai_tags,
        "overwrite_custom_metadata": overwrite_custom_metadata,
        "overwrite_file": overwrite_file,
        "overwrite_tags": overwrite_tags,
        "response_fields": response_fields,
        "tags": tags,
        "transformation": transformation,
        "use_unique_file_name": use_unique_file_name,
        "webhook_url": webhook_url,
    }

    filtered_body = {k: v for k, v in body.items() if v is not None}

    raw = await CLIENT.beta.v2.files.upload(**filtered_body)
    response = _serialize_upload_result(raw)

    return maybe_filter(filter_spec, response)


@tool(
    name="upload_v2_beta_files",
    description="Upload a file using ImageKit Upload API V2 (JWT-authenticated).",
)
async def upload_v2_beta_files_tool(
    file: Any,
    file_name: str,
    token: Optional[str] = None,
    checks: Optional[str] = None,
    custom_coordinates: Optional[str] = None,
    custom_metadata: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    extensions: Optional[Any] = None,
    folder: Optional[str] = None,
    is_private_file: Optional[bool] = None,
    is_published: Optional[bool] = None,
    overwrite_ai_tags: Optional[bool] = None,
    overwrite_custom_metadata: Optional[bool] = None,
    overwrite_file: Optional[bool] = None,
    overwrite_tags: Optional[bool] = None,
    response_fields: Optional[Sequence[str]] = None,
    tags: Optional[Sequence[str]] = None,
    transformation: Optional[Any] = None,
    use_unique_file_name: Optional[bool] = None,
    webhook_url: Optional[str] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Upload a file to ImageKit using the V2 Upload API.

    This API enhances security by validating the full upload payload using
    a server-generated JWT. It supports uploads via raw bytes, public URLs,
    or Base64-encoded data.

    Use this tool for:
    - Secure client-side uploads (JWT required)
    - Server-side uploads with strict payload integrity
    - Applying extensions (AI tagging, background removal, etc.)
    - Pre/post transformations at upload time

    Args:
        file: File content (binary, URL, or Base64 string).
        file_name: Name to assign to the uploaded file.
        token: JWT generated server-side (required for client-side uploads).
        checks: Optional server-side upload checks.
        custom_coordinates: Area of interest for images (`x,y,w,h`).
        custom_metadata: Custom metadata key-value pairs.
        description: Human-readable file description.
        extensions: Extensions to apply (e.g. auto-tagging, remove-bg).
        folder: Destination folder path.
        is_private_file: Whether the file should be private.
        is_published: Whether the file should be published immediately.
        overwrite_ai_tags: Whether to overwrite existing AI tags.
        overwrite_custom_metadata: Whether to overwrite existing metadata.
        overwrite_file: Whether to overwrite an existing file.
        overwrite_tags: Whether to overwrite existing tags.
        response_fields: Subset of response fields to include.
        tags: Tags to assign to the file.
        transformation: Pre/post upload transformations.
        use_unique_file_name: Whether to enforce unique filenames.
        webhook_url: Webhook to receive extension execution status.
        filter_spec: Optional glom-style filter specification used to
            reduce the response payload.

    Returns:
        A dictionary containing details of the uploaded file.
    """
    return await upload_v2_beta_files(
        file=file,
        file_name=file_name,
        token=token,
        checks=checks,
        custom_coordinates=custom_coordinates,
        custom_metadata=custom_metadata,
        description=description,
        extensions=extensions,
        folder=folder,
        is_private_file=is_private_file,
        is_published=is_published,
        overwrite_ai_tags=overwrite_ai_tags,
        overwrite_custom_metadata=overwrite_custom_metadata,
        overwrite_file=overwrite_file,
        overwrite_tags=overwrite_tags,
        response_fields=response_fields,
        tags=tags,
        transformation=transformation,
        use_unique_file_name=use_unique_file_name,
        webhook_url=webhook_url,
        filter_spec=filter_spec,
    )
