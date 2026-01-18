import logging
from typing import Dict, List, Optional, Literal, Any

from pydantic import BaseModel, Field, model_validator
from src.utils.utils import to_base64
from src.config import LOG_LEVEL

logger = logging.getLogger("transforms.ai_transforms")
logger.setLevel(LOG_LEVEL)


# ------------------------------------------------------------------
# Pydantic models
# ------------------------------------------------------------------


class AITransformOptions(BaseModel):
    """
    Validated parameters for ImageKit AI transformations.

    Mirrors the AI capabilities exposed by the URL builder:
    - Background operations (native and external)
    - Prompt-based edits and background changes
    - Generative fill
    - Drop shadow, retouch, and upscale
    """

    ai_background_removal_external: bool = False
    ai_remove_background: bool = False
    ai_edit: bool = False
    ai_changebg: bool = False
    ai_bg_genfill: bool = False
    ai_drop_shadow: bool = False
    ai_retouch: bool = False
    ai_upscale: bool = False

    az: Optional[int] = Field(215, ge=0)
    el: Optional[int] = Field(45, ge=0)
    st: Optional[int] = Field(60, ge=0)
    prompt: Optional[str] = None
    encoded: bool = False

    height: Optional[int] = Field(None, gt=0)
    width: Optional[int] = Field(None, gt=0)
    crop_mode: Literal["pad_resize", "pad_extract"] = "pad_resize"

    model_config = {"extra": "ignore"}

    @model_validator(mode="after")
    def validate_ai(self) -> "AITransformOptions":
        """
        Enforce prompt and dimension requirements and basic compatibility.
        """
        if self.ai_edit and not self.prompt:
            raise ValueError("ai_edit requires a non-empty prompt")

        if self.ai_changebg and not self.prompt:
            raise ValueError("ai_changebg requires a non-empty prompt")

        if self.ai_bg_genfill:
            if self.height is None or self.width is None:
                raise ValueError("ai_bg_genfill requires height and width")
            if self.crop_mode != "pad_resize":
                raise ValueError("ai_bg_genfill requires crop_mode='pad_resize'")

        if self.ai_drop_shadow:
            if self.az is not None and self.az < 0:
                raise ValueError("az must be >= 0")
            if self.el is not None and self.el < 0:
                raise ValueError("el must be >= 0")
            if self.st is not None and self.st < 0:
                raise ValueError("st must be >= 0")

        return self

    def to_transform_dicts(self) -> List[Dict[str, Any]]:
        """
        Serialize validated AI options into ImageKit transformation dicts.
        """
        transforms: List[Dict[str, Any]] = []
        dumped = self.model_dump()

        if dumped["ai_retouch"]:
            transforms.append({"e-retouch": True})

        if dumped["ai_upscale"]:
            transforms.append({"e-upscale": True})

        if dumped["ai_background_removal_external"]:
            transforms.append({"e-removedotbg": True})

        if dumped["ai_remove_background"]:
            transforms.append({"e-bgremove": True})

        if dumped["ai_edit"]:
            if dumped["encoded"]:
                transforms.append({"e-edit-prompte": to_base64(dumped["prompt"] or "")})
            else:
                transforms.append({"e-edit-prompt": dumped["prompt"]})

        if dumped["ai_changebg"]:
            if dumped["encoded"]:
                transforms.append({"e-changebg-prompte": to_base64(dumped["prompt"] or "")})
            else:
                transforms.append({"e-changebg-prompt": dumped["prompt"]})

        if dumped["ai_bg_genfill"]:
            genfill: Dict[str, Any] = {
                "bg": "genfill",
                "cm": dumped["crop_mode"],
                "h": dumped["height"],
                "w": dumped["width"],
            }
            transforms.append(genfill)

        if dumped["ai_drop_shadow"]:
            shadow: Dict[str, Any] = {"e-dropshadow": True}

            if not dumped["ai_background_removal_external"] and not dumped["ai_remove_background"]:
                transforms.append({"e-bgremove": True})

            if dumped["az"] is not None:
                shadow["az"] = dumped["az"]
            if dumped["el"] is not None:
                shadow["el"] = dumped["el"]
            if dumped["st"] is not None:
                shadow["st"] = dumped["st"]

            transforms.append(shadow)

        return transforms


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
        extras = {
            k: v for k, v in params.items() if k not in AITransformOptions.model_fields
        }
        if extras:
            logger.debug("Ignoring unsupported AI params: %s", extras)

        return self._ai_transform_impl(
            **{k: v for k, v in params.items() if k in AITransformOptions.model_fields}
        )

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
        az: Optional[int] = 215,
        el: Optional[int] = 45,
        st: Optional[int] = 60,
        prompt: Optional[str] = None,
        encoded: bool = False,
        height: Optional[int] = None,
        width: Optional[int] = None,
        crop_mode: Literal["pad_resize", "pad_extract"] = "pad_resize",
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

        ai_remove_background : bool
            Removes the background using ImageKit’s native AI.

        Image modification
        ~~~~~~~~~~~~~~~~~~
        ai_edit : bool
            Modifies an image using a text prompt.
            Requires `prompt`.
            - `e-edit-prompt` (plain text)
            - `e-edit-prompte` (base64-encoded)

        ai_changebg : bool
            Changes the background using a text prompt.
            Requires `prompt`.
            - `e-changebg-prompt`
            - `e-changebg-prompte`

        ai_bg_genfill : bool
            Extends or fills missing image areas using generative AI.
            Requires:
            - `crop_mode='pad_resize'`
            Optional:
            - `height`
            - `width`

        Visual effects
        ~~~~~~~~~~~~~~
        ai_drop_shadow : bool
            Adds an AI-generated drop shadow.
            The input image **must have a transparent background**.
            Optional parameters:
            - az (azimuth angle, >= 0)
            - el (elevation angle, >= 0)
            - st (shadow strength, >= 0)

        Enhancement
        ~~~~~~~~~~~
        ai_retouch : bool
            Improves visual quality by removing blemishes and artifacts.

        ai_upscale : bool
            Increases image resolution using AI.

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
        options = AITransformOptions(
            ai_background_removal_external=ai_background_removal_external,
            ai_remove_background=ai_remove_background,
            ai_edit=ai_edit,
            ai_changebg=ai_changebg,
            ai_bg_genfill=ai_bg_genfill,
            ai_drop_shadow=ai_drop_shadow,
            ai_retouch=ai_retouch,
            ai_upscale=ai_upscale,
            az=az,
            el=el,
            st=st,
            prompt=prompt,
            encoded=encoded,
            height=height,
            width=width,
            crop_mode=crop_mode,
        )

        return options.to_transform_dicts()
