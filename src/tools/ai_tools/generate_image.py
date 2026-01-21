import logging
import httpx
from typing import Any, Dict, List, Optional
from strands import tool
from urllib.parse import urlparse, quote

from src.tools.assets.list_assets import list_assets
from src.config import TIMEOUT_IMAGE_GENERATIO_SECONDS, LOG_LEVEL

logger = logging.getLogger("tools.generate_image")
logger.setLevel(LOG_LEVEL)

METADATA: Dict[str, Any] = {
    "resource": "generate_image",
    "operation": "read",
    "tags": [],
    "http_method": "post",
    "http_path": "/local/ik-genimg",
    "operation_id": "ik-genimg",
}


async def _probe_imagekit_url(
    url: str,
    timeout_seconds: int = 10,
) -> None:
    """
    Fire-and-forget probe to trigger ImageKit generation.

    Behavior:
    - 404 → error
    - 200 + is-intermediate-response:true → OK (still processing)
    - 200 normal → ready
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/135.0.0.0 Safari/537.36"
        )
    }
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            resp = await client.get(
                url,
                timeout=timeout_seconds,
                headers=headers,
            )

            # 404 means ImageKit rejected the request
            if resp.status_code == 404:
                logger.error("ImageKit generation failed (404): %s", url)
                raise RuntimeError("Generated image URL returned 404")

            # ImageKit intermediate response
            if resp.headers.get("is-intermediate-response") == "true":
                logger.info(
                    "ImageKit generation in progress (intermediate): %s",
                    url,
                )
                return {
                    "status": "processing",
                    "url": url,
                    "message": "Image generation in progress. For given url",
                }

            # Successful & ready
            if resp.status_code == 200:
                logger.info("ImageKit image ready: %s", url)
                return

            # Any other unexpected status
            logger.warning(
                "Unexpected ImageKit response %s for %s",
                resp.status_code,
                url,
            )

        except httpx.TimeoutException:
            # Timeout is OK — generation continues server-side
            logger.info(
                "ImageKit generation still in progress (timeout): %s",
                url,
            )


async def trigger_imagekit_generation(url: str) -> None:
    """
    Schedule ImageKit generation probe without blocking.
    """
    return await _probe_imagekit_url(
        url, timeout_seconds=TIMEOUT_IMAGE_GENERATIO_SECONDS
    )


@tool(
    name="imagekit_generate_image",
    description=(
        "Generate an image using ImageKit's ik-genimg (text-to-image) "
        "transformation. Returns a path-based ImageKit URL."
    ),
)
async def imagekit_generate_image(
    *,
    prompt: str,
    image_path: str,
) -> str:
    """
    Generate an image using ImageKit's ik-genimg transformation.

    Parameters
    ----------
    prompt : str
        Text prompt describing the image to generate. Required.

    image_path : str
        Output path for the generated image. This does not upload the image
        imagekit dam, its just the path appended to the ik-genimg URL
        for accessing the generated image. For saving the image to the DAM,
        you need to use upload tools separately.
        Example: 'gen-images/burger.jpg'

    Returns
    -------
    str
        A fully-qualified ImageKit URL using ik-genimg.
    """

    if not prompt or not prompt.strip():
        raise ValueError("prompt is required and must be non-empty")

    # -------------------------------------------------
    # Fetch any asset to discover ImageKit account ID
    # -------------------------------------------------
    files = await list_assets(
        type="file",
        limit=1,
        keys_to_filter=["url"],
    )

    if not files or "url" not in files[0]:
        raise ValueError("Unable to determine ImageKit account ID")

    sample_url = files[0]["url"]

    parsed = urlparse(sample_url)
    path_parts = parsed.path.strip("/").split("/")

    if not path_parts:
        raise ValueError("Invalid ImageKit asset URL")

    account_id = path_parts[0]

    # -------------------------------------------------
    # Build ik-genimg URL
    # -------------------------------------------------
    encoded_prompt = quote(prompt, safe="")

    base = f"{parsed.scheme}://{parsed.netloc}/{account_id}/"
    gen_image = f"{base}ik-genimg-prompt-{encoded_prompt}"

    if image_path:
        image_path = image_path.lstrip("/")
        gen_image = f"{gen_image}/{image_path}"

    logger.debug("Generated ImageKit ik-genimg URL: %s", gen_image)
    # ================ trigger generation =================
    await trigger_imagekit_generation(gen_image)
    return gen_image
