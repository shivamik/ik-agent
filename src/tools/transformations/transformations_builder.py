"""Utilities to build ImageKit transformation URLs from natural-language queries."""

from io import BytesIO
import logging
from typing import List, Dict, Any, Optional

import requests
from PIL import Image
from strands import tool

from src.clients import CLIENT
from src.config import LOG_LEVEL
from src.modules.ik_transforms.transformation_builder import resolve_imagekit_transform

METADATA: Dict[str, Any] = {
    "resource": "transformations.builder",
    "operation": "read",
    "tags": [],
    "http_method": "post",
    "http_path": "/local/transformation_builder",
    "operation_id": "transformation-builder",
}

DEFAULT_IMAGEKIT_SRC = "https://ik.imagekit.io/your_imagekit_id/default-image.jpg"
MAX_MP = 16  # Explicitly specified in ImageKit docs

logger = logging.getLogger("tools.transformation_builder")
logger.setLevel(LOG_LEVEL)


def handle_retouch_and_upscale(
    url: str,
    transformations: List[Dict[str, Any]],
) -> None:
    """
    Validate megapixel limits for e-retouch and e-upscale transformations.

    Rules enforced:
    - Applies only if 'e-retouch' or 'e-upscale' is present
    - Source URL must be reachable
    - Source must be a valid image
    - Image resolution must be < 16 megapixels

    Returns:
        None (no URL mutation)

    Raises:
        ValueError if validation fails
    """

    requires_check = any("e-retouch" in t or "e-upscale" in t for t in transformations)
    if not requires_check:
        return

    # -------------------------------------------------
    # Fetch image
    # -------------------------------------------------
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        raise ValueError(f"Source image is not reachable: {url}") from e

    content_type = resp.headers.get("Content-Type", "")
    if not content_type.startswith("image/"):
        raise ValueError(
            f"Source URL does not point to an image (Content-Type: {content_type})"
        )

    # -------------------------------------------------
    # Load image & compute megapixels
    # -------------------------------------------------
    try:
        img = Image.open(BytesIO(resp.content))
        width, height = img.size
    except Exception as e:
        raise ValueError("Source image is corrupt or unreadable") from e

    megapixels = (width * height) / 1_000_000

    if megapixels >= MAX_MP:
        raise ValueError(
            f"Image resolution {megapixels:.2f} MP exceeds "
            f"the maximum allowed limit of {MAX_MP} MP "
            f"for e-retouch / e-upscale"
        )

    return None


def preprocess_url(
    url: str,
    transformations: List[Dict[str, Any]],
) -> str:
    """
    Preprocess the source URL before ImageKit URL building.

    Currently handles:
    - ik-genimg path-based image generation
    - Resolution validation for e-retouch / e-upscale transformations
    """
    handle_retouch_and_upscale(url, transformations)

    return url


@tool(
    name="transformation-builder",
)
async def transformation_builder_tool(
    query: str,
    src: Optional[str] = DEFAULT_IMAGEKIT_SRC,
) -> str:
    """
    Build an ImageKit transformation URL from a natural-language image manipulation query.

    This tool interprets a user-provided query describing an image transformation
    (e.g. resizing, cropping, focusing, zooming, padding, or intelligent subject-based
    cropping) and converts it into a valid ImageKit transformation configuration.
    The resulting transformation is then applied to a source image URL to produce
    a fully-qualified ImageKit delivery URL.

    The tool is designed for **on-the-fly image manipulation** using ImageKit's
    URL-based transformation system and can be used in:
    - real-time image delivery
    - pre-rendered asset generation
    - upload-time or post-upload transformation pipelines

    The transformation generation process:
    1. Parses the natural-language query to infer intent.
    2. Resolves valid ImageKit transformation parameters using documented rules
        and constraints (e.g. crop modes, focus limitations, zoom restrictions).
    3. Normalizes and validates all parameters to ensure ImageKit compatibility.
    4. Constructs a transformation object suitable for ImageKit URL building.
    5. Builds the final transformed image URL using the ImageKit SDK.

    Parameters
    ----------
    query : str
        A natural-language description of the desired image transformation.
        Examples:
        - "Resize the image to 800x600 and focus on the face"
        - "Create a square thumbnail with auto focus"
        - "Crop the image from the center with 16:9 aspect ratio"
        - "Pad the image to 1200x1200 with a white background"

        The query must describe **what transformation is desired**, not how to
        construct the URL. Write detailed transformation and values required to
        carry out the transformations.

    src : str, optional
        The source imagekit file URL to which the transformation will be applied.
        The url should be from imagekit delivery domain.
        This must be a valid ImageKit-accessible image URL.
        Defaults to a placeholder ImageKit image.

    Returns
    -------
    str
        A string, the final transformed image URL. The structure is suitable for direct
        consumption by frontend or backend services that deliver images.

    Raises
    ------
    ValueError
        If the query cannot be resolved into a valid ImageKit transformation
        (e.g. unsupported parameters, conflicting options, or invalid combinations).
    """
    transformation = await resolve_imagekit_transform(query)
    src = src.split("?")[0]
    src = preprocess_url(src, transformation)
    url = await CLIENT.helper.build_url(
        src=src,
        transformation=transformation,
    )
    logger.debug(f"Built transformation URL: {url}")
    return url
