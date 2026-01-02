from typing import Any, Dict, Optional

from strands import tool

from src.clients import CLIENT
from src.utils import maybe_filter


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
    description="**Note:** This API is currently in beta.  \nCreates a new origin and returns the origin object.\n",
    inputSchema={
        "json": {
            "anyOf": [
                {
                    "properties": {
                        "access_key": {
                            "description": "Access key for the bucket.",
                            "type": "string",
                        },
                        "base_url_for_canonical_header": {
                            "description": "URL used in "
                            "the "
                            "Canonical "
                            "header (if "
                            "enabled).",
                            "type": "string",
                        },
                        "bucket": {"description": "S3 bucket name.", "type": "string"},
                        "include_canonical_header": {
                            "description": "Whether to send a Canonical header.",
                            "type": "boolean",
                        },
                        "name": {
                            "description": "Display name of the origin.",
                            "type": "string",
                        },
                        "prefix": {
                            "description": "Path prefix inside the bucket.",
                            "type": "string",
                        },
                        "secret_key": {
                            "description": "Secret key for the bucket.",
                            "type": "string",
                        },
                        "type": {"enum": ["S3"], "type": "string"},
                    },
                    "required": ["access_key", "bucket", "name", "secret_key", "type"],
                    "type": "object",
                },
                {
                    "properties": {
                        "access_key": {
                            "description": "Access key for the bucket.",
                            "type": "string",
                        },
                        "base_url_for_canonical_header": {
                            "description": "URL used in "
                            "the "
                            "Canonical "
                            "header (if "
                            "enabled).",
                            "type": "string",
                        },
                        "bucket": {"description": "S3 bucket name.", "type": "string"},
                        "endpoint": {
                            "description": "Custom S3-compatible endpoint.",
                            "type": "string",
                        },
                        "include_canonical_header": {
                            "description": "Whether to send a Canonical header.",
                            "type": "boolean",
                        },
                        "name": {
                            "description": "Display name of the origin.",
                            "type": "string",
                        },
                        "prefix": {
                            "description": "Path prefix inside the bucket.",
                            "type": "string",
                        },
                        "s3_force_path_style": {
                            "description": "Use path-style S3 URLs?",
                            "type": "boolean",
                        },
                        "secret_key": {
                            "description": "Secret key for the bucket.",
                            "type": "string",
                        },
                        "type": {"enum": ["S3_COMPATIBLE"], "type": "string"},
                    },
                    "required": [
                        "access_key",
                        "bucket",
                        "endpoint",
                        "name",
                        "secret_key",
                        "type",
                    ],
                    "type": "object",
                },
                {
                    "properties": {
                        "access_key": {
                            "description": "Access key for the bucket.",
                            "type": "string",
                        },
                        "base_url_for_canonical_header": {
                            "description": "URL used in "
                            "the "
                            "Canonical "
                            "header (if "
                            "enabled).",
                            "type": "string",
                        },
                        "bucket": {"description": "S3 bucket name.", "type": "string"},
                        "include_canonical_header": {
                            "description": "Whether to send a Canonical header.",
                            "type": "boolean",
                        },
                        "name": {
                            "description": "Display name of the origin.",
                            "type": "string",
                        },
                        "prefix": {
                            "description": "Path prefix inside the bucket.",
                            "type": "string",
                        },
                        "secret_key": {
                            "description": "Secret key for the bucket.",
                            "type": "string",
                        },
                        "type": {"enum": ["CLOUDINARY_BACKUP"], "type": "string"},
                    },
                    "required": ["access_key", "bucket", "name", "secret_key", "type"],
                    "type": "object",
                },
                {
                    "properties": {
                        "base_url": {
                            "description": "Root URL for the web folder origin.",
                            "type": "string",
                        },
                        "base_url_for_canonical_header": {
                            "description": "URL used in "
                            "the "
                            "Canonical "
                            "header (if "
                            "enabled).",
                            "type": "string",
                        },
                        "forward_host_header_to_origin": {
                            "description": "Forward the Host header to origin?",
                            "type": "boolean",
                        },
                        "include_canonical_header": {
                            "description": "Whether to send a Canonical header.",
                            "type": "boolean",
                        },
                        "name": {
                            "description": "Display name of the origin.",
                            "type": "string",
                        },
                        "type": {"enum": ["WEB_FOLDER"], "type": "string"},
                    },
                    "required": ["base_url", "name", "type"],
                    "type": "object",
                },
                {
                    "properties": {
                        "base_url_for_canonical_header": {
                            "description": "URL used in "
                            "the "
                            "Canonical "
                            "header (if "
                            "enabled).",
                            "type": "string",
                        },
                        "include_canonical_header": {
                            "description": "Whether to send a Canonical header.",
                            "type": "boolean",
                        },
                        "name": {
                            "description": "Display name of the origin.",
                            "type": "string",
                        },
                        "type": {"enum": ["WEB_PROXY"], "type": "string"},
                    },
                    "required": ["name", "type"],
                    "type": "object",
                },
                {
                    "properties": {
                        "base_url_for_canonical_header": {
                            "description": "URL used in "
                            "the "
                            "Canonical "
                            "header (if "
                            "enabled).",
                            "type": "string",
                        },
                        "bucket": {"type": "string"},
                        "client_email": {"type": "string"},
                        "include_canonical_header": {
                            "description": "Whether to send a Canonical header.",
                            "type": "boolean",
                        },
                        "name": {
                            "description": "Display name of the origin.",
                            "type": "string",
                        },
                        "prefix": {"type": "string"},
                        "private_key": {"type": "string"},
                        "type": {"enum": ["GCS"], "type": "string"},
                    },
                    "required": [
                        "bucket",
                        "client_email",
                        "name",
                        "private_key",
                        "type",
                    ],
                    "type": "object",
                },
                {
                    "properties": {
                        "account_name": {"type": "string"},
                        "base_url_for_canonical_header": {
                            "description": "URL used in "
                            "the "
                            "Canonical "
                            "header (if "
                            "enabled).",
                            "type": "string",
                        },
                        "container": {"type": "string"},
                        "include_canonical_header": {
                            "description": "Whether to send a Canonical header.",
                            "type": "boolean",
                        },
                        "name": {
                            "description": "Display name of the origin.",
                            "type": "string",
                        },
                        "prefix": {"type": "string"},
                        "sas_token": {"type": "string"},
                        "type": {"enum": ["AZURE_BLOB"], "type": "string"},
                    },
                    "required": [
                        "account_name",
                        "container",
                        "name",
                        "sas_token",
                        "type",
                    ],
                    "type": "object",
                },
                {
                    "properties": {
                        "base_url": {
                            "description": "Akeneo instance base URL.",
                            "type": "string",
                        },
                        "base_url_for_canonical_header": {
                            "description": "URL used in "
                            "the "
                            "Canonical "
                            "header (if "
                            "enabled).",
                            "type": "string",
                        },
                        "client_id": {
                            "description": "Akeneo API client ID.",
                            "type": "string",
                        },
                        "client_secret": {
                            "description": "Akeneo API client secret.",
                            "type": "string",
                        },
                        "include_canonical_header": {
                            "description": "Whether to send a Canonical header.",
                            "type": "boolean",
                        },
                        "name": {
                            "description": "Display name of the origin.",
                            "type": "string",
                        },
                        "password": {
                            "description": "Akeneo API password.",
                            "type": "string",
                        },
                        "type": {"enum": ["AKENEO_PIM"], "type": "string"},
                        "username": {
                            "description": "Akeneo API username.",
                            "type": "string",
                        },
                    },
                    "required": [
                        "base_url",
                        "client_id",
                        "client_secret",
                        "name",
                        "password",
                        "type",
                        "username",
                    ],
                    "type": "object",
                },
            ],
            "type": "object",
        }
    },
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
    """
    Create a new origin (beta).

    Prefer `filter_spec` to reduce response size when possible.
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
