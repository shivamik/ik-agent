from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


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


@tool(name="upload_v2_beta_files")
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
    """
    Upload a file using the ImageKit V2 Upload API (beta), which verifies the
    entire request payload using a JSON Web Token (JWT).

    This API supports secure server-side and client-side uploads and provides
    advanced options such as pre/post transformations, extensions, overwrite
    controls, and webhook notifications.

    ⚠️ This API is currently in beta.

    --- Security & Authentication ---

    - Server-side uploads authenticate using your private API key.
    - Client-side uploads require a short-lived, single-use JWT (`token`)
      generated on a secure server using your private API key.
    - Reusing a JWT will result in a validation error, even if a previous
      request failed.

    --- File Input ---

    The `file` parameter accepts one of the following:
    - Raw binary data (multipart/form-data)
    - A publicly accessible HTTP/HTTPS URL (must respond within 8 seconds)
    - A Base64-encoded string or data URI

    --- Limits ---

    File size limits depend on your plan:
    - Free plan:
      - Images / audio / raw files: up to 20 MB
      - Videos: up to 100 MB
    - Paid plans:
      - Images / audio / raw files: up to 40 MB
      - Videos: up to 2 GB

    A single file can have a maximum of 100 versions.

    --- Args ---

    file:
        The file to upload. Can be binary data, a public URL, or a Base64 string.

    file_name:
        The name under which the file will be stored in ImageKit.

    token:
        Client-generated JWT used for secure client-side uploads.
        Required only when uploading directly from a client.
        Must be generated server-side using the private API key.

    checks:
        Server-side validation checks to run on the asset.
        See ImageKit Upload API checks documentation for details.

    folder:
        Destination folder path for the uploaded file.
        Nested folders are created automatically if they do not exist.

    tags:
        List of tags to associate with the asset.
        If omitted and the file is overwritten, existing tags are removed.
        Total combined tag length must not exceed 500 characters.

    custom_metadata:
        Key-value pairs of custom metadata to attach to the asset.
        Custom metadata fields must exist before assigning values.
        If omitted on overwrite, existing metadata may be removed.

    description:
        Optional text description of the file contents.

    custom_coordinates:
        Area of interest for image files, specified as "x,y,width,height".
        If omitted during overwrite, existing coordinates are removed.

    is_private_file:
        Whether to mark the uploaded file as private.
        Private files require signed URLs or named transformations for access.

    is_published:
        Whether the file should be published immediately.
        Unpublished files are only accessible via the Media Library.
        Draft uploads are available only on certain enterprise plans.

    overwrite_file:
        Controls overwrite behavior when a file with the same name exists.
        If False and use_unique_file_name is False, the upload fails.

    overwrite_tags:
        If True and tags are not provided, existing tags are removed.

    overwrite_ai_tags:
        If True and the file exists, existing AI tags are removed.

    overwrite_custom_metadata:
        If True and custom_metadata is not provided, existing metadata is removed.

    use_unique_file_name:
        If True, ImageKit appends a unique suffix to the file name.
        If False, the provided file_name is used as-is.

    transformation:
        Pre- and post-upload transformations.
        - pre: applied before storing the file
        - post: applied immediately after upload (e.g., thumbnails, video encodes)

    extensions:
        Extensions to apply to the asset (e.g., background removal,
        auto-tagging, AI auto-description).

    response_fields:
        List of additional fields to include in the API response.
        Supported values include:
        - tags, customCoordinates, isPrivateFile, isPublished,
          customMetadata, metadata, selectedFieldsSchema

    webhook_url:
        Endpoint that receives a POST request with the final status
        of extensions after processing completes.

    filter_spec:
        Optional glom specification used to project or reshape the
        response payload returned by the API.

        Example:
        - "url"
        - {"id": "fileId", "url": "url"}

    --- Returns ---

    A dictionary containing details of the uploaded file, optionally
    filtered using `filter_spec`.
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
