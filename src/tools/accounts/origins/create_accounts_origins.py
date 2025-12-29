import os
from typing import Optional, Literal, Dict, Any

from strands import tool
from src.clients import client


# ---------------------------------------------------------------------------
# CORE FUNCTION (pure Python, unit-test this)
# ---------------------------------------------------------------------------

def create_imagekit_origin(
    *,
    type: Literal[
        "S3",
        "S3_COMPATIBLE",
        "CLOUDINARY_BACKUP",
        "WEB_FOLDER",
        "WEB_PROXY",
        "GCS",
        "AZURE_BLOB",
        "AKENEO_PIM",
    ],
    name: str,

    # Shared / optional
    base_url: Optional[str] = None,
    base_url_for_canonical_header: Optional[str] = None,
    include_canonical_header: Optional[bool] = None,
    prefix: Optional[str] = None,

    # S3 / S3-compatible / Cloudinary
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    bucket: Optional[str] = None,
    endpoint: Optional[str] = None,
    s3_force_path_style: Optional[bool] = None,

    # GCS
    client_email: Optional[str] = None,
    private_key: Optional[str] = None,

    # Azure Blob
    account_name: Optional[str] = None,
    container: Optional[str] = None,
    sas_token: Optional[str] = None,

    # Akeneo
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Core function:
    - No Strands dependency
    - Safe to unit-test
    - Calls ImageKit Admin SDK
    """

    kwargs: Dict[str, Any] = {
        "type": type,
        "name": name,
    }

    # Shared optional fields
    if base_url_for_canonical_header is not None:
        kwargs["base_url_for_canonical_header"] = base_url_for_canonical_header
    if include_canonical_header is not None:
        kwargs["include_canonical_header"] = include_canonical_header
    if prefix is not None:
        kwargs["prefix"] = prefix

    # -------------------------
    # Validation + mapping
    # -------------------------

    if type in {"S3", "CLOUDINARY_BACKUP"}:
        for k in ("access_key", "secret_key", "bucket"):
            if locals()[k] is None:
                raise ValueError(f"{type} origin requires `{k}`")
        kwargs.update(
            access_key=access_key,
            secret_key=secret_key,
            bucket=bucket,
        )

    elif type == "S3_COMPATIBLE":
        for k in ("access_key", "secret_key", "bucket", "endpoint"):
            if locals()[k] is None:
                raise ValueError("S3_COMPATIBLE requires access_key, secret_key, bucket, endpoint")
        kwargs.update(
            access_key=access_key,
            secret_key=secret_key,
            bucket=bucket,
            endpoint=endpoint,
        )
        if s3_force_path_style is not None:
            kwargs["s3_force_path_style"] = s3_force_path_style

    elif type == "WEB_FOLDER":
        if not base_url:
            raise ValueError("WEB_FOLDER requires base_url")
        kwargs["base_url"] = base_url

    elif type == "WEB_PROXY":
        pass

    elif type == "GCS":
        for k in ("bucket", "client_email", "private_key"):
            if locals()[k] is None:
                raise ValueError("GCS requires bucket, client_email, private_key")
        kwargs.update(
            bucket=bucket,
            client_email=client_email,
            private_key=private_key,
        )

    elif type == "AZURE_BLOB":
        for k in ("account_name", "container", "sas_token"):
            if locals()[k] is None:
                raise ValueError("AZURE_BLOB requires account_name, container, sas_token")
        kwargs.update(
            account_name=account_name,
            container=container,
            sas_token=sas_token,
        )

    elif type == "AKENEO_PIM":
        for k in ("base_url", "client_id", "client_secret", "username", "password"):
            if locals()[k] is None:
                raise ValueError(
                    "AKENEO_PIM requires base_url, client_id, client_secret, username, password"
                )
        kwargs.update(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
        )

    # -------------------------
    # SDK call
    # -------------------------

    try:
        origin = client.accounts.origins.create(**kwargs)
        return origin.model_dump() if hasattr(origin, "model_dump") else dict(origin)
    except Exception as e:
        raise RuntimeError(f"ImageKit API error: {e}")


# ---------------------------------------------------------------------------
# STRANDS TOOL WRAPPER (thin, optional)
# ---------------------------------------------------------------------------


tool(
    name="create_imagekit_origin",
    description="Create an ImageKit origin using the Admin API.",
)(create_imagekit_origin)
