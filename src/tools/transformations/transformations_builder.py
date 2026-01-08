from typing import Any, Dict, Optional
from strands import tool

from src.modules.ik_transforms.transformation_builder import resolve_imagekit_transform
from src.clients import CLIENT


METADATA: Dict[str, Any] = {
    "resource": "transformations.builder",
    "operation": "read",
    "tags": [],
    "http_method": "post",
    "http_path": "/local/transformation_builder",
    "operation_id": "transformation-builder",
}


@tool(
    name="transformation-builder",
)
async def transformation_builder_tool(
    query: str,
    src: Optional[str] = "https://ik.imagekit.io/your_imagekit_id/default-image.jpg",
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
        The source image URL to which the transformation will be applied.
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
    url = await CLIENT.helper.build_url(
        src=src,
        transformation=transformation,
    )
    return url
