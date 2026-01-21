"""
resize_and_crop_transforms.py

Validated Resize & Crop transformation module for ImageKit.

This module is designed to be a **parameter validation and normalization layer**.
It does not build URLs directly; instead it returns a transformation dict using
ImageKit short keys (e.g., "w", "h", "cm", "c") that a URL builder can serialize.

Why this exists
---------------
ImageKit resize/crop-related parameters are **context-sensitive**:

- `crop_mode` (cm) controls padding vs extraction behavior.
- `crop` (c) controls resize/crop strategy.
- `focus` (fo) has different allowed values depending on `crop_mode` / `crop`.
- Coordinates (`x`, `y`, `x_center`, `y_center`) are only valid for certain crop modes.

This module enforces those constraints to prevent invalid transformation URLs.

Supported parameters in this module
-----------------------------------
Sizing / crop primitives:
- width (w)
- height (h)
- aspect_ratio (ar)
- crop (c)
- crop_mode (cm)

Crop behavior modifiers:
- focus (fo)  [context-dependent validation]
- zoom (z)    [validated as positive; also blocked for crop='force']

Positioning:
- x, y, x_center, y_center  [only for cm in {"extract","pad_extract"}; absolute vs relative exclusive]

Output density:
- dpr

Notes
-----
- The COCO class list below is included explicitly (80 standard COCO classes),
  because ImageKit allows `fo` to be set to COCO object class names for intelligent focus.
- This module is intentionally strict. If you want "lenient" mode, you can add a flag
  to downgrade errors to warnings.

Example
-------
Basic usage in a URL builder:

```python
tx = ResizeAndCropTransforms().resize_and_crop(
    width=800,
    height=600,
    crop_mode="extract",
    focus="auto",
)
# -> {"w": "800", "h": "600", "cm": "extract", "fo": "auto"}
```
"""

import logging
from typing import Any, ClassVar, Dict, Optional, Union, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
    field_validator,
)

from src.utils.utils import get_transform_key
from src.config import LOG_LEVEL, COCO_CLASSES
from src.modules.ik_transforms.types import (
    BackgroundValue,
    CROP_MODES,
    CROP,
    AspectRatioValue,
    Background,
    NumberOrExpression,
    AspectRatio,
)

logger = logging.getLogger("transforms.resize_and_crop")
logger.setLevel(LOG_LEVEL)


class ResizeAndCrop(BaseModel):
    """
    Pydantic model for ImageKit resize & crop parameters.

    Use `.to_transform_dict()` to get the short-key dict consumed by the URL builder.
    """

    model_config = ConfigDict(extra="ignore")

    # -------------------------------------------------
    # DIMENSIONS / CROP
    # -------------------------------------------------
    width: Optional[NumberOrExpression] = None
    height: Optional[NumberOrExpression] = None
    aspect_ratio: Optional[Union[AspectRatioValue, AspectRatio]] = None
    crop: Optional[CROP] = "maintain_ratio"
    crop_mode: Optional[CROP_MODES] = None

    # -------------------------------------------------
    # BEHAVIOR MODIFIERS
    # -------------------------------------------------
    focus: Optional[str] = None
    zoom: Optional[NumberOrExpression] = None

    # -------------------------------------------------
    # POSITIONING
    # -------------------------------------------------
    x: Optional[NumberOrExpression] = None
    y: Optional[NumberOrExpression] = None
    x_center: Optional[NumberOrExpression] = None
    y_center: Optional[NumberOrExpression] = None

    # -------------------------------------------------
    # OUTPUT DENSITY / BACKGROUND
    # -------------------------------------------------
    dpr: Optional[NumberOrExpression] = None
    background: Optional[Union[BackgroundValue, Background]] = None

    COCO_CLASSES: ClassVar = COCO_CLASSES
    _PAD_RESIZE_FO: ClassVar[set[str]] = {"left", "right", "top", "bottom"}
    _EXTRACT_RELATIVE_FO: ClassVar[set[str]] = {
        "center",
        "top",
        "bottom",
        "left",
        "right",
        "top_left",
        "top_right",
        "bottom_left",
        "bottom_right",
    }
    _SPECIAL_FO: ClassVar[set[str]] = {"custom"}
    _INTELLIGENT_FO: ClassVar[set[str]] = {"auto", "face"}

    # -------------------------------------------------
    # Field-level validation
    # -------------------------------------------------
    @field_validator("width", "height", "zoom", "dpr")
    @classmethod
    def validate_positive_numeric_or_expr(cls, v: Optional[NumberOrExpression], info):
        if v is None:
            return v

        if isinstance(v, (int, float)):
            if v <= 0:
                raise ValueError(f"{info.field_name} must be > 0")
            return v

        if isinstance(v, str) and v.strip():
            return v

        raise ValueError(
            f"{info.field_name} must be a positive number or non-empty string"
        )

    # -------------------------------------------------
    # Semantic validation
    # -------------------------------------------------
    @model_validator(mode="after")
    def validate_semantics(self) -> "ResizeAndCrop":
        # Focus & zoom cannot be used with crop='force'
        if self.crop == "force":
            if self.focus is not None:
                raise ValueError("focus (fo) cannot be used when crop='force'")
            if self.zoom is not None:
                raise ValueError("zoom (z) cannot be used when crop='force'")

        # Positioning restrictions
        if any(v is not None for v in (self.x, self.y, self.x_center, self.y_center)):
            if self.crop_mode not in {"extract", "pad_extract"}:
                raise ValueError(
                    "x, y, x_center, y_center are only allowed with crop_mode='extract' or 'pad_extract'"
                )

            if (self.x is not None or self.y is not None) and (
                self.x_center is not None or self.y_center is not None
            ):
                raise ValueError(
                    "Cannot mix absolute offsets (x,y) with center offsets (x_center,y_center)"
                )

        # Focus validation (context-dependent)
        if self.focus is not None:
            allowed_focus = set()

            if self.crop_mode == "pad_resize":
                allowed_focus.update(self._PAD_RESIZE_FO)
                allowed_focus.update(self._INTELLIGENT_FO)
                allowed_focus.update(self.COCO_CLASSES)

            if self.crop_mode in {"extract", "pad_extract"}:
                allowed_focus.update(self._EXTRACT_RELATIVE_FO)
                allowed_focus.update(self._SPECIAL_FO)
                allowed_focus.update(self._INTELLIGENT_FO)
                allowed_focus.update(self.COCO_CLASSES)

            if self.crop == "maintain_ratio":
                allowed_focus.update(self._SPECIAL_FO)
                allowed_focus.update(self._INTELLIGENT_FO)
                allowed_focus.update(self.COCO_CLASSES)

            if not allowed_focus:
                raise ValueError(
                    "focus (fo) is only valid with crop_mode='pad_resize', crop='maintain_ratio', "
                    "or crop_mode in {'extract','pad_extract'}"
                )

            if self.focus not in allowed_focus:
                raise ValueError(f"Invalid focus (fo) value: {self.focus!r}")

        return self

    # -------------------------------------------------
    # Normalization
    # -------------------------------------------------
    def to_transform_dict(self) -> Dict[str, Any]:
        dumped = self.model_dump(exclude_none=True)
        transforms: Dict[str, Any] = {}

        if "width" in dumped:
            transforms[get_transform_key("w")] = str(dumped["width"])

        if "height" in dumped:
            transforms[get_transform_key("h")] = str(dumped["height"])

        if "aspect_ratio" in dumped:
            aspect_ratio = (
                self.aspect_ratio
                if isinstance(self.aspect_ratio, AspectRatio)
                else AspectRatio.from_raw(self.aspect_ratio)
            )
            transforms[get_transform_key("ar")] = aspect_ratio.to_ik_params()

        if "crop" in dumped:
            transforms[get_transform_key("c")] = dumped["crop"]

        if "crop_mode" in dumped:
            transforms[get_transform_key("cm")] = dumped["crop_mode"]

        if "focus" in dumped:
            transforms[get_transform_key("fo")] = dumped["focus"]

        if "zoom" in dumped:
            transforms[get_transform_key("z")] = str(dumped["zoom"])

        if "x" in dumped:
            transforms[get_transform_key("x")] = str(dumped["x"])

        if "y" in dumped:
            transforms[get_transform_key("y")] = str(dumped["y"])

        if "x_center" in dumped:
            transforms[get_transform_key("x_center")] = str(dumped["x_center"])

        if "y_center" in dumped:
            transforms[get_transform_key("y_center")] = str(dumped["y_center"])

        if "dpr" in dumped:
            transforms[get_transform_key("dpr")] = str(dumped["dpr"])

        if "background" in dumped:
            background = (
                self.background
                if isinstance(self.background, Background)
                else Background.from_raw(self.background)
            )
            transforms["background"] = background.to_ik_params()

        return transforms


class ResizeAndCropTransforms:
    """
    A validated transformation spec for ImageKit resize & crop parameters.

    Public API:
        resize_and_crop(...)-> Dict[str, str]

    The returned dict uses ImageKit's short keys:
        w, h, ar, c, cm, fo, z, x, y, x_center, y_center, dpr
    """

    def resize_and_crop(
        self,
        **params: Any,
    ) -> Dict[str, str]:
        known_fields = set(ResizeAndCrop.model_fields.keys())
        known = {k: v for k, v in params.items() if k in known_fields}
        extra = {k: v for k, v in params.items() if k not in known_fields}

        if extra:
            logger.debug("Ignoring unsupported params: %s", extra)

        return self._resize_and_crop_impl(**known)

    def _resize_and_crop_impl(
        self,
        *,
        width: Optional[NumberOrExpression] = None,
        height: Optional[NumberOrExpression] = None,
        aspect_ratio: Optional[Union[AspectRatioValue, AspectRatio]] = None,
        crop: Optional[
            Literal["force", "at_max_enlarge", "at_least", "maintain_ratio"]
        ] = "maintain_ratio",
        crop_mode: Optional[Literal["pad_resize", "pad_extract", "extract"]] = None,
        focus: Optional[str] = None,
        zoom: Optional[NumberOrExpression] = None,
        x: Optional[NumberOrExpression] = None,
        y: Optional[NumberOrExpression] = None,
        x_center: Optional[NumberOrExpression] = None,
        y_center: Optional[NumberOrExpression] = None,
        dpr: Optional[NumberOrExpression] = None,
        background: Optional[Union[BackgroundValue, Background]] = None,
        **kwargs,
    ) -> Dict[str, str]:
        """
        Validate and normalize ImageKit resize & crop parameters.

        Parameters
        ----------
        width : int | float | str, optional
            Output width. Accepts:
            - int/float > 0
            - string tokens like "auto"
            - arithmetic expressions as strings (passed through)

        height : int | float | str, optional
            Output height. Same acceptance as width.

        aspect_ratio : str, optional
            Aspect ratio as "<w>_<h>" (e.g. "16_9") or an arithmetic expression string.
            `iar_div_2` or `car_mul_0.75`. For eg aspect ratio of 16:9 is represented as "16_9".

        crop : {"force","at_max_enlarge","at_least","maintain_ratio"}, optional
            Default: "maintain_ratio"
            Forced Crop (c-force): Enforces exact dimensions in the output image, but no cropping to achieve the requested size.
                Forcefully resizes image. Aspect ratio may not be preserved.
            Max-size Crop (c-at_max): Preserves the whole image content without cropping if the maximum dimension is less than the
                requested size, modifying the image’s dimensions to maintain the aspect ratio.
                Larger dimension is matched to the requested size. other dimension is scaled to maintain aspect ratio.
            Max-size Enlarge Crop (c-at_max_enlarge): Preserves the whole image content without cropping if the maximum dimension is less than the
                requested size, modifying the image’s dimensions to maintain the aspect ratio. Same as at_max but allows upscaling.
                Larger dimension is matched to the requested size. other dimension is scaled to maintain aspect ratio.
            Min-size Crop (c-at_least): Similar to max-size crop but works to ensure that the output image size
                does not go below specified dimensions, maintaining the aspect ratio.
                Smaller dimension is matched to the requested size. other dimension is scaled to maintain aspect ratio.
            Maintain Ratio Crop (c-maintain_ratio): Ensures the aspect ratio is preserved while cropping, potentially
                adjusting one of the dimensions.

            Resize/crop strategy. Important:
            - When crop='force', focus and zoom are not allowed.

        crop_mode : {"pad_resize","pad_extract","extract"}, optional
            Crop mode controlling padding/extraction.
            - Coordinates (x,y,x_center,y_center) are ONLY allowed with crop_mode in {"extract","pad_extract"}.
            Pad Resize Crop (cm-pad_resize): Preserves the entire image content without cropping while ensuring the
                dimensions you specified are met, using padding to fill any empty space if necessary.
            Extract Crop (cm-extract): Crops a smaller area from the larger original image based on specified
                coordinates. This can also be combined with focus parameters to ensure important areas of the
                image are prioritized during cropping.
            Pad Extract Crop (cm-pad_extract): An extension of the extract crop strategy that allows for extracting
                a larger area than the original image, adding solid color padding around it to meet the requested size.

        background:
            - For Solid color, requires hex, RGBA hex or svg color name
            - For dominant color background, use "dominant"
            - For blurred background use
                background: {"blur_intensity": Union[int] = "auto", brightness: [-255 to 255]}
            - For Gradient background use
                background: {"mode": "dominant", "pallete_size": Literal[2,4]=2}

        focus : str, optional
            Focus parameter `fo` with context-sensitive values.
            For tight crop around objects, use COCO class names (e.g., "person", "dog").
            `fo-<object_class>`
            Use fo-left to push object to left side when using crop_mode='pad_resize', allowing padding to right.
            Use fo-right to push object to right side when using crop_mode='pad_resize', allowing padding to left.
            Use fo-top to push object to top side when using crop_mode='pad_resize', allowing padding to bottom.

        zoom : int | float | str, optional
            Zoom factor `z`. Must be > 0 when numeric.
            Forbidden when crop='force'.
            Zoom > 1 means zoom in
            Zoom < 1 means zoom out

        x, y : int | float | str, optional
            Absolute offsets (top-left origin) used for extraction crops.
            Allowed only when crop_mode in {"extract","pad_extract"}.
            Cannot be mixed with x_center/y_center.

        x_center, y_center : int | float | str, optional
            Center offsets used for extraction crops.
            Allowed only when crop_mode in {"extract","pad_extract"}.
            Cannot be mixed with x/y.

        dpr : int | float | str, optional
            Device pixel ratio. Must be > 0 when numeric.

        Returns
        -------
        Dict[str, str]
            A dict with ImageKit short transformation keys.

        Raises
        ------
        ValueError
            If parameters are invalid or in conflict.
        """

        if kwargs:
            logger.debug("Ignoring unsupported params: %s", kwargs)

        return ResizeAndCrop(
            width=width,
            height=height,
            aspect_ratio=aspect_ratio,
            crop=crop,
            crop_mode=crop_mode,
            focus=focus,
            zoom=zoom,
            x=x,
            y=y,
            x_center=x_center,
            y_center=y_center,
            dpr=dpr,
            background=background,
        ).to_transform_dict()
