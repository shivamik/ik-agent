from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils.utils import maybe_filter


METADATA: Dict[str, Any] = {
    "resource": "accounts.origins",
    "operation": "write",
    "tags": [],
    "http_method": "post",
    "http_path": "/v1/accounts/origins",
    "operation_id": "create-origin",
}


def _serialize_origin(result: Any) -> Dict[str, Any]:
    """
    Normalize SDK responses into plain dicts.
    """
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return dict(result)


async def create_accounts_origins(
    *,
    type: str,
    name: str,
    access_key: Optional[str] = None,
    account_name: Optional[str] = None,
    base_url: Optional[str] = None,
    base_url_for_canonical_header: Optional[str] = None,
    bucket: Optional[str] = None,
    client_email: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    container: Optional[str] = None,
    endpoint: Optional[str] = None,
    forward_host_header_to_origin: Optional[bool] = None,
    include_canonical_header: Optional[bool] = None,
    password: Optional[str] = None,
    prefix: Optional[str] = None,
    private_key: Optional[str] = None,
    s3_force_path_style: Optional[bool] = None,
    sas_token: Optional[str] = None,
    secret_key: Optional[str] = None,
    username: Optional[str] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Create a new origin (beta).

    Accepts parameters for S3, S3-compatible, Cloudinary backup, web folder,
    web proxy, GCS, Azure Blob, and Akeneo PIM origins. Use `filter_spec`
    (glom spec) to shrink the response payload.
    """
    body = {
        "type": type,
        "name": name,
        "access_key": access_key,
        "account_name": account_name,
        "base_url": base_url,
        "base_url_for_canonical_header": base_url_for_canonical_header,
        "bucket": bucket,
        "client_email": client_email,
        "client_id": client_id,
        "client_secret": client_secret,
        "container": container,
        "endpoint": endpoint,
        "forward_host_header_to_origin": forward_host_header_to_origin,
        "include_canonical_header": include_canonical_header,
        "password": password,
        "prefix": prefix,
        "private_key": private_key,
        "s3_force_path_style": s3_force_path_style,
        "sas_token": sas_token,
        "secret_key": secret_key,
        "username": username,
    }
    filtered_body = {k: v for k, v in body.items() if v is not None}

    raw = await CLIENT.accounts.origins.create(**filtered_body)
    response = _serialize_origin(raw)
    return maybe_filter(filter_spec, response)


@tool(
    name="create_accounts_origins",
    description="Create a new origin for an account (beta).",
)
async def create_accounts_origins_tool(
    type: str,
    name: str,
    access_key: Optional[str] = None,
    account_name: Optional[str] = None,
    base_url: Optional[str] = None,
    base_url_for_canonical_header: Optional[str] = None,
    bucket: Optional[str] = None,
    client_email: Optional[str] = None,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    container: Optional[str] = None,
    endpoint: Optional[str] = None,
    forward_host_header_to_origin: Optional[bool] = None,
    include_canonical_header: Optional[bool] = None,
    password: Optional[str] = None,
    prefix: Optional[str] = None,
    private_key: Optional[str] = None,
    s3_force_path_style: Optional[bool] = None,
    sas_token: Optional[str] = None,
    secret_key: Optional[str] = None,
    username: Optional[str] = None,
    filter_spec: Optional[Any] = None,
) -> Dict[str, Any]:
    """Create a new origin (beta).

    This API supports multiple origin types. The required parameters
    depend on the selected `type`.

    Supported origin types and key fields:

    - **S3**
      Required: access_key, secret_key, bucket, name
      Optional: prefix, include_canonical_header, base_url_for_canonical_header

    - **S3_COMPATIBLE**
      Required: access_key, secret_key, bucket, endpoint, name
      Optional: prefix, s3_force_path_style, include_canonical_header

    - **CLOUDINARY_BACKUP**
      Required: access_key, secret_key, bucket, name

    - **WEB_FOLDER**
      Required: base_url, name
      Optional: forward_host_header_to_origin, include_canonical_header

    - **WEB_PROXY**
      Required: name

    - **GCS**
      Required: bucket, client_email, private_key, name
      Optional: prefix, include_canonical_header

    - **AZURE_BLOB**
      Required: account_name, container, sas_token, name
      Optional: prefix, include_canonical_header

    - **AKENEO_PIM**
      Required: base_url, client_id, client_secret, username, password, name

    The backend API validates required fields based on `type`.

    Use `filter_spec` to reduce response size when possible.
    """
    return await create_accounts_origins(
        type=type,
        name=name,
        access_key=access_key,
        account_name=account_name,
        base_url=base_url,
        base_url_for_canonical_header=base_url_for_canonical_header,
        bucket=bucket,
        client_email=client_email,
        client_id=client_id,
        client_secret=client_secret,
        container=container,
        endpoint=endpoint,
        forward_host_header_to_origin=forward_host_header_to_origin,
        include_canonical_header=include_canonical_header,
        password=password,
        prefix=prefix,
        private_key=private_key,
        s3_force_path_style=s3_force_path_style,
        sas_token=sas_token,
        secret_key=secret_key,
        username=username,
        filter_spec=filter_spec,
    )
