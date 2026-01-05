"""
Utilities for resolving image inputs from bytes, paths, or URLs.
"""

import io
import os
import mimetypes
import requests
from pathlib import Path
from typing import Union
from urllib.parse import urlparse

from PIL import Image


FileInput = Union[str, bytes, Path]


class FileResolutionError(ValueError):
    """Raised when an image input cannot be resolved or validated."""

    pass


def _is_url(value: str) -> bool:
    """Return True if the string looks like an HTTP/HTTPS URL."""
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _download_and_validate_image(
    url: str,
    *,
    output_dir: Path,
    timeout: int,
) -> Path:
    """Download an image URL to output_dir and validate its bytes."""
    try:
        resp = requests.get(url, stream=True, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise FileResolutionError(f"Image URL unreachable: {url}") from e

    content_type = resp.headers.get("Content-Type", "")
    if not content_type.startswith("image/"):
        raise FileResolutionError(
            f"URL does not point to an image (Content-Type: {content_type})"
        )

    suffix = mimetypes.guess_extension(content_type) or ".img"
    filename = Path(urlparse(url).path).name or "downloaded_image"
    path = output_dir / f"{filename}{suffix}"

    data = resp.content

    _validate_image_bytes(data)

    path.write_bytes(data)
    return path


def _validate_image_bytes(data: bytes) -> None:
    """Verify that image bytes can be opened and validated."""
    try:
        with Image.open(io.BytesIO(data)) as img:
            img.verify()  # does not decode fully, but checks integrity
    except Exception as e:
        raise FileResolutionError("Corrupt or invalid image bytes") from e


def _validate_image_path(path: Path) -> None:
    """Verify that a file path points to a valid image."""
    try:
        with Image.open(path) as img:
            img.verify()
    except Exception as e:
        raise FileResolutionError(f"Corrupt or invalid image file: {path}") from e


def resolve_image_input(
    file: FileInput,
    *,
    output_dir: Path,
    timeout: int = 10,
) -> Union[bytes, Path]:
    """Normalize an image input into bytes or a local path.

    Args:
        file: Image bytes, a local path, or an HTTP/HTTPS URL.
        output_dir: Where to store downloaded URL files.
        timeout: Timeout in seconds for URL downloads.

    Returns:
        Bytes for in-memory inputs, or a Path for local/URL files.

    Raises:
        FileResolutionError: If the input is unreachable, invalid, or unsupported.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------
    # 1. Bytes
    # ------------------
    if isinstance(file, (bytes, bytearray)):
        _validate_image_bytes(file)
        return bytes(file)

    # ------------------
    # 2. PathLike
    # ------------------
    if isinstance(file, os.PathLike):
        path = Path(file)
        if not path.exists():
            raise FileResolutionError(f"File does not exist: {path}")
        _validate_image_path(path)
        return path

    # ------------------
    # 3. URL (string)
    # ------------------
    if isinstance(file, str) and _is_url(file):
        return _download_and_validate_image(
            file,
            output_dir=output_dir,
            timeout=timeout,
        )

    # ------------------
    # Unsupported
    # ------------------
    raise FileResolutionError(f"Unsupported file input type: {type(file).__name__}")
