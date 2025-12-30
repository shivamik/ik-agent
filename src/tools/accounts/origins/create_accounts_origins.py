from __future__ import annotations

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
            "type": "object",
            "anyOf": [
                {
                    "type": "object",
                    "properties": {
                        "accessKey": {
                            "type": "string",
                            "description": "Access key for the bucket.",
                        },
                        "bucket": {
                            "type": "string",
                            "description": "S3 bucket name.",
                        },
                        "name": {
                            "type": "string",
                            "description": "Display name of the origin.",
                        },
                        "secretKey": {
                            "type": "string",
                            "description": "Secret key for the bucket.",
                        },
                        "type": {
                            "type": "string",
                            "enum": ["S3"],
                        },
                        "baseUrlForCanonicalHeader": {
                            "type": "string",
                            "description": "URL used in the Canonical header (if enabled).",
                        },
                        "includeCanonicalHeader": {
                            "type": "boolean",
                            "description": "Whether to send a Canonical header.",
                        },
                        "prefix": {
                            "type": "string",
                            "description": "Path prefix inside the bucket.",
                        },
                    },
                    "required": ["accessKey", "bucket", "name", "secretKey", "type"],
                },
                {
                    "type": "object",
                    "properties": {
                        "accessKey": {
                            "type": "string",
                            "description": "Access key for the bucket.",
                        },
                        "bucket": {
                            "type": "string",
                            "description": "S3 bucket name.",
                        },
                        "endpoint": {
                            "type": "string",
                            "description": "Custom S3-compatible endpoint.",
                        },
                        "name": {
                            "type": "string",
                            "description": "Display name of the origin.",
                        },
                        "secretKey": {
                            "type": "string",
                            "description": "Secret key for the bucket.",
                        },
                        "type": {
                            "type": "string",
                            "enum": ["S3_COMPATIBLE"],
                        },
                        "baseUrlForCanonicalHeader": {
                            "type": "string",
                            "description": "URL used in the Canonical header (if enabled).",
                        },
                        "includeCanonicalHeader": {
                            "type": "boolean",
                            "description": "Whether to send a Canonical header.",
                        },
                        "prefix": {
                            "type": "string",
                            "description": "Path prefix inside the bucket.",
                        },
                        "s3ForcePathStyle": {
                            "type": "boolean",
                            "description": "Use path-style S3 URLs?",
                        },
                    },
                    "required": [
                        "accessKey",
                        "bucket",
                        "endpoint",
                        "name",
                        "secretKey",
                        "type",
                    ],
                },
                {
                    "type": "object",
                    "properties": {
                        "accessKey": {
                            "type": "string",
                            "description": "Access key for the bucket.",
                        },
                        "bucket": {
                            "type": "string",
                            "description": "S3 bucket name.",
                        },
                        "name": {
                            "type": "string",
                            "description": "Display name of the origin.",
                        },
                        "secretKey": {
                            "type": "string",
                            "description": "Secret key for the bucket.",
                        },
                        "type": {
                            "type": "string",
                            "enum": ["CLOUDINARY_BACKUP"],
                        },
                        "baseUrlForCanonicalHeader": {
                            "type": "string",
                            "description": "URL used in the Canonical header (if enabled).",
                        },
                        "includeCanonicalHeader": {
                            "type": "boolean",
                            "description": "Whether to send a Canonical header.",
                        },
                        "prefix": {
                            "type": "string",
                            "description": "Path prefix inside the bucket.",
                        },
                    },
                    "required": ["accessKey", "bucket", "name", "secretKey", "type"],
                },
                {
                    "type": "object",
                    "properties": {
                        "baseUrl": {
                            "type": "string",
                            "description": "Root URL for the web folder origin.",
                        },
                        "name": {
                            "type": "string",
                            "description": "Display name of the origin.",
                        },
                        "type": {
                            "type": "string",
                            "enum": ["WEB_FOLDER"],
                        },
                        "baseUrlForCanonicalHeader": {
                            "type": "string",
                            "description": "URL used in the Canonical header (if enabled).",
                        },
                        "forwardHostHeaderToOrigin": {
                            "type": "boolean",
                            "description": "Forward the Host header to origin?",
                        },
                        "includeCanonicalHeader": {
                            "type": "boolean",
                            "description": "Whether to send a Canonical header.",
                        },
                    },
                    "required": ["baseUrl", "name", "type"],
                },
                {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Display name of the origin.",
                        },
                        "type": {
                            "type": "string",
                            "enum": ["WEB_PROXY"],
                        },
                        "baseUrlForCanonicalHeader": {
                            "type": "string",
                            "description": "URL used in the Canonical header (if enabled).",
                        },
                        "includeCanonicalHeader": {
                            "type": "boolean",
                            "description": "Whether to send a Canonical header.",
                        },
                    },
                    "required": ["name", "type"],
                },
                {
                    "type": "object",
                    "properties": {
                        "bucket": {
                            "type": "string",
                        },
                        "clientEmail": {
                            "type": "string",
                        },
                        "name": {
                            "type": "string",
                            "description": "Display name of the origin.",
                        },
                        "privateKey": {
                            "type": "string",
                        },
                        "type": {
                            "type": "string",
                            "enum": ["GCS"],
                        },
                        "baseUrlForCanonicalHeader": {
                            "type": "string",
                            "description": "URL used in the Canonical header (if enabled).",
                        },
                        "includeCanonicalHeader": {
                            "type": "boolean",
                            "description": "Whether to send a Canonical header.",
                        },
                        "prefix": {
                            "type": "string",
                        },
                    },
                    "required": ["bucket", "clientEmail", "name", "privateKey", "type"],
                },
                {
                    "type": "object",
                    "properties": {
                        "accountName": {
                            "type": "string",
                        },
                        "container": {
                            "type": "string",
                        },
                        "name": {
                            "type": "string",
                            "description": "Display name of the origin.",
                        },
                        "sasToken": {
                            "type": "string",
                        },
                        "type": {
                            "type": "string",
                            "enum": ["AZURE_BLOB"],
                        },
                        "baseUrlForCanonicalHeader": {
                            "type": "string",
                            "description": "URL used in the Canonical header (if enabled).",
                        },
                        "includeCanonicalHeader": {
                            "type": "boolean",
                            "description": "Whether to send a Canonical header.",
                        },
                        "prefix": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "accountName",
                        "container",
                        "name",
                        "sasToken",
                        "type",
                    ],
                },
                {
                    "type": "object",
                    "properties": {
                        "baseUrl": {
                            "type": "string",
                            "description": "Akeneo instance base URL.",
                        },
                        "clientId": {
                            "type": "string",
                            "description": "Akeneo API client ID.",
                        },
                        "clientSecret": {
                            "type": "string",
                            "description": "Akeneo API client secret.",
                        },
                        "name": {
                            "type": "string",
                            "description": "Display name of the origin.",
                        },
                        "password": {
                            "type": "string",
                            "description": "Akeneo API password.",
                        },
                        "type": {
                            "type": "string",
                            "enum": ["AKENEO_PIM"],
                        },
                        "username": {
                            "type": "string",
                            "description": "Akeneo API username.",
                        },
                        "baseUrlForCanonicalHeader": {
                            "type": "string",
                            "description": "URL used in the Canonical header (if enabled).",
                        },
                        "includeCanonicalHeader": {
                            "type": "boolean",
                            "description": "Whether to send a Canonical header.",
                        },
                    },
                    "required": [
                        "baseUrl",
                        "clientId",
                        "clientSecret",
                        "name",
                        "password",
                        "type",
                        "username",
                    ],
                },
            ],
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
