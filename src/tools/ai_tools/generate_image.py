from typing import Any, Dict, List, Optional
from strands import tool
from urllib.parse import urlparse, quote

from src.clients import CLIENT
from src.utils.utils import maybe_filter
from src.tools.assets.list_assets import list_assets


METADATA: Dict[str, Any] = {
    "resource": "generate_image",
    "operation": "read",
    "tags": [],
    "http_method": "post",
    "http_path": "/local/ik-genimg",
    "operation_id": "ik-genimg",
}


@tool(
    name="imagekit-generate-image",
    description=(
        "Generate an image using ImageKit's ik-genimg (text-to-image) "
        "transformation. Returns a path-based ImageKit URL."
    ),
)
async def imagekit_generate_image(
    *,
    prompt: str,
    image_path: Optional[str] = None,
) -> str:
    """
    Generate an image using ImageKit's ik-genimg transformation.

    Parameters
    ----------
    prompt : str
        Text prompt describing the image to generate. Required.

    image_path : str, optional
        Output path for the generated image.
        Example: 'gen-images/burger.jpg'
        If omitted, only the ik-genimg prompt path is returned.

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
        filter_spec=[{"url": "url"}],
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
    genimg_base = f"{base}ik-genimg-prompt-{encoded_prompt}"

    if image_path:
        image_path = image_path.lstrip("/")
        return f"{genimg_base}/{image_path}"

    return genimg_base
