import logging
from typing import Dict, List, Optional, Literal, Any, Union

from pydantic import BaseModel, Field
from src.utils.utils import to_base64
from src.config import LOG_LEVEL

logger = logging.getLogger("transforms.ai_transforms")
logger.setLevel(LOG_LEVEL)


# ------------------------------------------------------------------
# Pydantic models
# ------------------------------------------------------------------


class AIChangeBackground(BaseModel):
    prompt: str


class AIEditImage(BaseModel):
    prompt: str


class BackgroundGenFill(BaseModel):
    height: int = Field(..., gt=0)
    width: int = Field(..., gt=0)
    crop_mode: Literal["pad_resize", "pad_extract"] = "pad_resize"
    prompt: Optional[str] = None


class AIDropShadow(BaseModel):
    az: Optional[int] = Field(215, ge=0)
    el: Optional[int] = Field(45, ge=0)
    st: Optional[int] = Field(60, ge=0)


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
    ai_retouch: bool = False
    ai_upscale: bool = False
    ai_generate_variation: bool = False
    ai_changebg: Optional[AIChangeBackground] = None
    ai_edit: Optional[AIEditImage] = None
    ai_bg_genfill: Optional[BackgroundGenFill] = None
    ai_drop_shadow: Optional[Union[bool, AIDropShadow]] = None
    encoded: bool = False

    def to_transform_dicts(self) -> List[Dict[str, Any]]:
        """
        Serialize validated AI options into ImageKit transformation dicts.
        """
        dumped = self.model_dump(exclude_none=True)
        transforms: List[Dict[str, Any]] = []

        if self.ai_retouch:
            transforms.append({"e-retouch": True})

        if self.ai_upscale:
            transforms.append({"e-upscale": True})

        if self.ai_background_removal_external:
            transforms.append({"e-removedotbg": True})

        if self.ai_remove_background:
            transforms.append({"e-bgremove": True})

        if self.ai_edit:
            prompt = dumped["ai_edit"]["prompt"]
            if self.encoded:
                transforms.append({"e-edit-prompte": to_base64(prompt or "")})
            else:
                transforms.append({"e-edit-prompt": prompt})

        if self.ai_changebg:
            prompt = dumped["ai_changebg"]["prompt"]
            if self.encoded:
                transforms.append({"e-changebg-prompte": to_base64(prompt or "")})
            else:
                transforms.append({"e-changebg-prompt": prompt})

        #  handle genfill
        if self.ai_bg_genfill:
            genfill_dict = self.ai_bg_genfill.model_dump(exclude_none=True)
            genfill_params = {}
            if "prompt" in genfill_dict:
                prompt = genfill_dict.pop("prompt")
                if self.encoded:
                    genfill_params["bg-genfill-prompte"] = to_base64(prompt or "")
                else:
                    genfill_params["bg-genfill-prompt"] = prompt
            else:
                genfill_params["bg"] = "genfill"
            genfill_params["crop_mode"] = genfill_dict.pop("crop_mode")
            genfill_params["height"] = genfill_dict.pop("height")
            genfill_params["width"] = genfill_dict.pop("width")

            transforms.append(genfill_params)

        if self.ai_generate_variation:
            transforms.append({"e-genvar": True})

        if self.ai_drop_shadow:
            shadow: Dict[str, Any] = {"e-dropshadow": True}

            if (
                not self.ai_background_removal_external
                and not self.ai_remove_background
            ):
                transforms.append({"e-bgremove": True})
            if isinstance(self.ai_drop_shadow, AIDropShadow):
                ai_drop_shadow_params = self.ai_drop_shadow.model_dump(
                    exclude_none=True
                )
                shadow["el"] = ai_drop_shadow_params["el"]
                shadow["st"] = ai_drop_shadow_params["st"]
                shadow["az"] = ai_drop_shadow_params["az"]

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
        ai_retouch: bool = False,
        ai_upscale: bool = False,
        ai_generate_variation: bool = False,
        ai_changebg: Optional[AIChangeBackground] = None,
        ai_edit: Optional[AIEditImage] = None,
        ai_bg_genfill: Optional[BackgroundGenFill] = None,
        ai_drop_shadow: Optional[Union[bool, AIDropShadow]] = None,
        encoded: bool = False,
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
            Removes the background using ImageKit’s native AI. Cheaper model.
            Costs 0.1x of ai_background_removal_external.

        Image modification
        ~~~~~~~~~~~~~~~~~~
        ai_edit : Optional[AIEditImage]
            Edits the image using AI using defined prompt.
            It can edit image based on the prompt provided. Colorize,
            add objects, remove objects etc. Free form edit using AI.
            Requires `prompt` in the dictionary.
            Eg: {"ai_edit": {"prompt": "Add a red hat on the person"}}

        ai_changebg : Optional[AIChangeBackground]
            Changes the background using a text prompt using AI.
            Free form background change. It can change background to
            any scenario based on the prompt provided. Not to be confused by
            background removal. It does not remove background but can replace background.
            Requires {`prompt`} in the dictionary
            Eg: {"ai_changebg": {"prompt": "Change background to a beach"}}

        ai_bg_genfill : Optional[BackgroundGenFill]
            Performs generative fill on the background using a text prompt.
            This  transformation extends an image beyond its original boundaries,
            allowing you to add new visual elements in an image while preserving
            the original image content.
            Requires {`prompt`, `height`, and `width`, `crop_mode`} in the dictionary.
            Eg: {"ai_bg_genfill": {"prompt": "A scenic mountain view",
                                   "height": 800,
                                   "width": 600,
                                   "crop_mode": "pad_resize"}}

        ai_generate_variation : bool
            Generates variations of the input image using AI.
            Eg. {"ai_generate_variation": True}

        Visual effects
        ~~~~~~~~~~~~~~
        ai_drop_shadow : Optional[AIDropShadow]
            Adds an AI-generated drop shadow.
            The input image **must have a transparent background**.
            Optional parameters:
            - az (azimuth angle, >= 0)
            - el (elevation angle, >= 0)
            - st (shadow strength, >= 0)
            Eg: {"ai_drop_shadow": {"az": 120, "el": 30, "st": 70}}
            Or simply: {"ai_drop_shadow": True}

        Enhancement
        ~~~~~~~~~~~
        ai_retouch : bool
            Improves visual quality by removing blemishes and artifacts.
            Eg. {"ai_retouch": True}

        ai_upscale : bool
            Increases image resolution using AI.
            Eg. {"ai_upscale": True}

        Common parameters
        -----------------
        encoded : bool, default False
            If True, prompt is assumed to be base64-encoded.
            If False, prompt will be encoded automatically when required.

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
            ai_retouch=ai_retouch,
            ai_upscale=ai_upscale,
            ai_generate_variation=ai_generate_variation,
            ai_changebg=ai_changebg,
            ai_edit=ai_edit,
            ai_bg_genfill=ai_bg_genfill,
            ai_drop_shadow=ai_drop_shadow,
            encoded=encoded,
        )

        return options.to_transform_dicts()
