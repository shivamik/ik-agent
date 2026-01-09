import logging
from typing import Dict, List, Optional, Literal, TypedDict, Any

from src.utils.utils import to_base64

logger = logging.getLogger("transforms.ai_transforms")
logger.setLevel(logging.DEBUG)


# ------------------------------------------------------------------
# Typed params (mirror of ResizeAndCropParams pattern)
# ------------------------------------------------------------------
print(logger)


class AITransformParams(TypedDict, total=False):
    ai_background_removal_external: bool
    ai_remove_background: bool
    ai_edit: bool
    ai_changebg: bool
    ai_bg_genfill: bool
    ai_drop_shadow: bool
    ai_retouch: bool
    ai_upscale: bool
    ai_image_generation: bool

    az: Optional[int]
    el: Optional[int]
    st: Optional[int]
    prompt: Optional[str]
    encoded: bool

    height: int
    width: int
    crop_mode: Literal["pad_resize", "pad_extract"]

    ai_image_path: Optional[str]


# ------------------------------------------------------------------
# Public class (mirror of ResizeAndCropTransforms)
# ------------------------------------------------------------------


class AITransforms:
    """
    A validated transformation spec for ImageKit AI transformations.

    Public API:
        ai_transform(**params) -> List[Dict[str, Any]]
    """

    def ai_transform(self, **params: Any) -> List[Dict[str, Any]]:
        """
        Public wrapper.
        Filters known params and ignores unsupported ones.
        """

        known: AITransformParams = {}
        extra: Dict[str, Any] = {}

        for k, v in params.items():
            if k in AITransformParams.__annotations__:
                known[k] = v
            else:
                extra[k] = v

        if extra:
            logger.debug("Ignoring unsupported AI params: %s", extra)

        return self._ai_transform_impl(**known)

    # ------------------------------------------------------------------
    # Core implementation (already written by you)
    # ------------------------------------------------------------------

    def _ai_transform_impl(
        self,
        ai_background_removal_external: bool = False,
        ai_remove_background: bool = False,
        ai_edit: bool = False,
        ai_changebg: bool = False,
        ai_bg_genfill: bool = False,
        ai_drop_shadow: bool = False,
        ai_retouch: bool = False,
        ai_upscale: bool = False,
        ai_image_generation: bool = False,
        az: Optional[int] = 215,
        el: Optional[int] = 45,
        st: Optional[int] = 60,
        prompt: Optional[str] = None,
        encoded: bool = False,
        height: Optional[int] = None,
        width: Optional[int] = None,
        crop_mode: Literal["pad_resize", "pad_extract"] = "pad_resize",
        ai_image_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Validate and normalize ImageKit AI transformation parameters.

        This method validates **AI-powered, asynchronous ImageKit transformations**
        and returns a list of **normalized transformation dictionaries**.
        It does NOT build URLs or chain transformations itself.

        Each returned dictionary represents **one AI transformation step**.
        Multiple steps must later be chained using `:` (never `,`) by the URL builder.

        Important behavioral rules
        --------------------------
        - AI transformations are **asynchronous and expensive**.
        - Outputs are **cached indefinitely** and consume **extension units**.
        - Multiple AI operations are allowed, but MUST be applied as separate
        - Use ai_remove_background=True for most background removal tasks. Unless
            you specifically want to use external service or some high quality output.
        transformation steps.
        - Some AI transformations have **strict prerequisites** such as:
            - transparent backgrounds
            - specific crop modes
            - mandatory prompts
            - path-based generation

        Supported AI transformations
        ----------------------------

        Background & foreground
        ~~~~~~~~~~~~~~~~~~~~~~~
        ai_background_removal_external : bool
            Removes the background using an Removedotbg (external AI service).
            Normalized as: `e-removedotbg`.

        ai_remove_background : bool
            Removes the background using ImageKit’s native AI.
            Normalized as: `e-bgremove`.

        Image modification
        ~~~~~~~~~~~~~~~~~~
        ai_edit : bool
            Modifies an image using a text prompt.
            Requires `prompt`.
            Normalized as:
            - `e-edit-prompt` (plain text)
            - `e-edit-prompte` (base64-encoded)

        ai_changebg : bool
            Changes the background using a text prompt.
            Requires `prompt`.
            Normalized as:
            - `e-changebg-prompt`
            - `e-changebg-prompte`

        ai_bg_genfill : bool
            Extends or fills missing image areas using generative AI.
            Requires:
            - `crop_mode='pad_resize'`
            Optional:
            - `height`
            - `width`
            Normalized as: `{ "bg": "genfill", "h": <height>, "w": <width>, "cm": "pad_resize" }`

        Visual effects
        ~~~~~~~~~~~~~~
        ai_drop_shadow : bool
            Adds an AI-generated drop shadow.
            The input image **must have a transparent background**.
            Optional parameters:
            - az (azimuth angle, >= 0)
            - el (elevation angle, >= 0)
            - st (shadow strength, >= 0)
            Normalized as: `e-dropshadow`.

        Enhancement
        ~~~~~~~~~~~
        ai_retouch : bool
            Improves visual quality by removing blemishes and artifacts.
            Normalized as: `e-retouch`.

        ai_upscale : bool
            Increases image resolution using AI.
            Normalized as: `e-upscale`.

        Generation
        ~~~~~~~~~~
        ai_image_generation : bool
            Generates a new image from a text prompt.
            This is a **path-based transformation**, not a query-based one.
            Requires:
            - `prompt`
            - `ai_image_path`
            Normalized as:
            - `ik-genimg-prompt`
            - `ik-genimg-path`

        Common parameters
        -----------------
        prompt : str, optional
            Text prompt required for edit, background change, and generation.
            Must be non-empty.

        encoded : bool, default False
            If True, prompt is assumed to be base64-encoded.
            If False, prompt will be encoded automatically when required.

        height : int, optional
            Output height for generative fill.
            Must be > 0.

        width : int, optional
            Output width for generative fill.
            Must be > 0.

        crop_mode : {"pad_resize","pad_extract"}, default "pad_resize"
            Crop mode used for compatibility checks.
            `bg-genfill` requires `pad_resize`.

        Returns
        -------
        List[Dict[str, Any]]
            A list of normalized AI transformation dictionaries.
            Each dict represents one transformation step.

        Raises
        ------
        ValueError
            If:
            - required prompts are missing
            - invalid dimensions are provided
            - crop mode constraints are violated
            - image generation parameters are incomplete
            - no AI transformation is specified
        """

        transforms: List[Dict[str, Any]] = []

        # -------------------------------------------------
        # Background removal (external)
        # -------------------------------------------------
        if ai_background_removal_external:
            transforms.append({"e-removedotbg": True})

        # -------------------------------------------------
        # Background removal (ImageKit)
        # -------------------------------------------------
        if ai_remove_background:
            transforms.append({"e-bgremove": True})

        # -------------------------------------------------
        # AI Edit
        # -------------------------------------------------
        if ai_edit:
            if not prompt:
                raise ValueError("ai_edit requires a non-empty prompt")

            if encoded:
                transforms.append({"e-edit-prompte": to_base64(prompt)})
            else:
                transforms.append({"e-edit-prompt": prompt})

        # -------------------------------------------------
        # Change background
        # -------------------------------------------------
        if ai_changebg:
            if not prompt:
                raise ValueError("ai_changebg requires a non-empty prompt")

            if encoded:
                transforms.append({"e-changebg-prompte": to_base64(prompt)})
            else:
                transforms.append({"e-changebg-prompt": prompt})

        # -------------------------------------------------
        # Background generative fill
        # -------------------------------------------------
        if ai_bg_genfill:
            genfill: Dict[str, Any] = {"bg": "genfill"}
            if height is None or width is None:
                raise ValueError("ai_bg_genfill requires height and width")

            if height is not None:
                if height <= 0:
                    raise ValueError("height must be > 0")
                genfill["h"] = height

            if width is not None:
                if width <= 0:
                    raise ValueError("width must be > 0")
                genfill["w"] = width

            genfill["cm"] = crop_mode
            transforms.append(genfill)

        # -------------------------------------------------
        # Drop shadow
        # -------------------------------------------------
        if ai_drop_shadow:
            shadow: Dict[str, Any] = {"e-dropshadow": True}

            if not ai_background_removal_external and not ai_remove_background:
                transforms.append({"e-bgremove": True})

            if az is not None:
                if az < 0:
                    raise ValueError("az must be >= 0")
                shadow["az"] = az

            if el is not None:
                if el < 0:
                    raise ValueError("el must be >= 0")
                shadow["el"] = el

            if st is not None:
                if st < 0:
                    raise ValueError("st must be >= 0")
                shadow["st"] = st

            transforms.append(shadow)

        # -------------------------------------------------
        # Retouch
        # -------------------------------------------------
        if ai_retouch:
            transforms.append({"e-retouch": True})

        # -------------------------------------------------
        # Upscale
        # -------------------------------------------------
        if ai_upscale:
            transforms.append({"e-upscale": True})

        # -------------------------------------------------
        # Image generation (path-based)
        # -------------------------------------------------
        if ai_image_generation:
            if not ai_image_path:
                raise ValueError("ai_image_path is required for ai_image_generation")
            if not prompt:
                raise ValueError("prompt is required for ai_image_generation")

            transforms.append(
                {
                    "ik-genimg-prompt": (to_base64(prompt) if not encoded else prompt),
                    "ik-genimg-path": ai_image_path,
                }
            )

        return transforms
