"""
transforms.py

Validated Effects & Enhancements transformation model for ImageKit.

This module:
- Validates effect parameters
- Normalizes them into ImageKit-compatible transformation dicts
- Does NOT build URLs
"""

import logging
from typing import Optional, Dict, Any, Literal, List, Union
from pydantic import BaseModel, Field, model_validator, field_validator

from ..types import (
    NumberOrExpression,
    POSITION,
    Color,
    Number,
    FlipMode,
    Background,
    BackgroundValue,
)

from src.config import LOG_LEVEL

logger = logging.getLogger("transforms.effects_and_enhancement")
logger.setLevel(LOG_LEVEL)


class UnsharpMaskEffect(BaseModel):
    """Sharpening kernel parameters for `e-unsharp_mask`."""

    radius: float = Field(..., gt=0)
    sigma: float = Field(..., gt=0)
    amount: float = Field(..., gt=0)
    threshold: float = Field(..., gt=0)


class ShadowEffect(BaseModel):
    """Shadow parameters for `e-shadow-<blur>_<saturation>_<x-offset>_<y-offset>`."""

    blur: int = Field(10, ge=0, le=15)
    saturation: int = Field(30, ge=0, le=100)
    x_offset: int = Field(2, ge=-100, le=100)
    y_offset: int = Field(2, ge=-100, le=100)


class GradientEffect(BaseModel):
    """Gradient overlay parameters for `e-gradient`."""

    linear_direction: Optional[Union[int, POSITION]] = 180
    from_color: Optional[Color] = "FFFFFF"
    to_color: Optional[Color] = "00000000"
    stop_point: Optional[Union[float, NumberOrExpression]] = 1

    @field_validator("linear_direction")
    def validate_linear_direction(cls, v):
        if isinstance(v, int) and not (0 <= v <= 360):
            raise ValueError("linear_direction must be between 0 and 360")
        return v


class PerspectiveDistortEffect(BaseModel):
    """Perspective warp coordinates for `e-distort` (p-x1_y1_x2_y2_x3_y3_x4_y4)."""

    x1: Number
    y1: Number
    x2: Number
    y2: Number
    x3: Number
    y3: Number
    x4: Number
    y4: Number


class ArcDistortEffect(BaseModel):
    """Arc distortion degrees for `e-distort=a-<degrees>`."""

    degrees: Number


class BorderEffect(BaseModel):
    """Border width/color for `b` transform."""

    border_width: NumberOrExpression
    color: Color


class ColorReplaceEffect(BaseModel):
    """Color replacement parameters for `cr`."""

    to_color: Color
    tolerance: int = Field(35, ge=0, le=100)
    from_color: Optional[Color] = None


# -------------------------------------------------------------------
# Main Effects class
# -------------------------------------------------------------------


class Effects(BaseModel):
    """
    Validated set of ImageKit effect and enhancement parameters.

    Each field maps to either an `e-*` effect or a regular transform.
    Use `to_transform_dicts()` to emit ImageKit-ready dictionaries.
    """

    # e-* effects
    contrast: Optional[bool] = None
    sharpen: Optional[Union[bool, int]] = Field(None, ge=0)
    grayscale: Optional[bool] = None

    unsharp_mask: Optional[UnsharpMaskEffect] = None
    shadow: Optional[Union[bool, ShadowEffect]] = None
    gradient: Optional[Union[bool, GradientEffect]] = None
    perspective_distort: Optional[PerspectiveDistortEffect] = None
    arc_distort: Optional[ArcDistortEffect] = None
    color_replace: Optional[ColorReplaceEffect] = None

    # non-e transforms
    border: Optional[BorderEffect] = None
    blur: Optional[int] = Field(None, ge=1, le=100)
    trim: Optional[Union[Literal[True], int]] = None
    rotate: Optional[Union[NumberOrExpression, Literal["auto"]]] = None
    flip: Optional[FlipMode] = None
    radius: Optional[Union[NumberOrExpression, Literal["max"]]] = None
    background: Optional[Union[BackgroundValue, Background]] = None
    opacity: Optional[int] = Field(None, ge=0, le=100)

    # -------------------------------------------------
    # Semantic validation
    # -------------------------------------------------
    @model_validator(mode="after")
    def validate_effects(self) -> "Effects":
        if isinstance(self.trim, int) and not (1 <= self.trim <= 99):
            raise ValueError("trim must be between 1 and 99")

        return self

    @field_validator("trim")
    def validate_trim(cls, v):
        if isinstance(v, int) and not (1 <= v <= 99):
            raise ValueError("trim must be between 1 and 99")
        return v

    # -------------------------------------------------
    # Normalization
    # -------------------------------------------------
    def to_transform_dicts(self) -> list[Dict[str, Any]]:
        """
        Convert validated model into a list of ImageKit transformation dicts.
        """
        transforms: list[Dict[str, Any]] = []
        dumped = self.model_dump(exclude_none=True)

        # -----------------------------
        # e-* effects
        # -----------------------------
        if dumped.get("contrast"):
            transforms.append({"e": "contrast"})

        if "sharpen" in dumped:
            transforms.append(
                {"e": "sharpen"}
                if dumped["sharpen"] == 0
                else {"e-sharpen": dumped["sharpen"]}
            )

        if dumped.get("grayscale"):
            transforms.append({"e": "grayscale"})

        if "unsharp_mask" in dumped:
            transforms.append(dumped["unsharp_mask"])

        if "shadow" in dumped:
            if dumped["shadow"] is True:
                transforms.append({"e": "shadow"})
            else:
                shadow_params = dumped["shadow"]
                transforms.append(
                    {
                        "e-shadow": (
                            f"bl-{shadow_params['blur']}_"
                            f"st-{shadow_params['saturation']}_"
                            f"x-{shadow_params['x_offset']}_"
                            f"y-{shadow_params['y_offset']}"
                        )
                    }
                )

        if "gradient" in dumped:
            if dumped["gradient"] is True:
                transforms.append({"e": "gradient"})
            else:
                gradient_params = dumped["gradient"]
                transforms.append(
                    {
                        "e-gradient": (
                            f"ld-{gradient_params['linear_direction']}_"
                            f"from-{gradient_params['from_color']}_"
                            f"to-{gradient_params['to_color']}_"
                            f"sp-{gradient_params['stop_point']}"
                        )
                    }
                )

        if "perspective_distort" in dumped:
            perspective_distort_params = dumped["perspective_distort"]
            corners = "p-{}_{}_{}_{}_{}_{}_{}_{}".format(
                perspective_distort_params["x1"],
                perspective_distort_params["y1"],
                perspective_distort_params["x2"],
                perspective_distort_params["y2"],
                perspective_distort_params["x3"],
                perspective_distort_params["y3"],
                perspective_distort_params["x4"],
                perspective_distort_params["y4"],
            )
            transforms.append(
                {
                    "e-distort": corners,
                }
            )

        if "arc_distort" in dumped:
            arc_distort_params = dumped["arc_distort"]
            transforms.append(
                {
                    "e-distort": f"a-{arc_distort_params['degrees']}",
                }
            )

        if "color_replace" in dumped:
            if "from_color" in dumped["color_replace"]:
                value = (
                    f"{dumped['color_replace']['from_color']}_"
                    f"{dumped['color_replace']['tolerance']}_"
                    f"{dumped['color_replace']['to_color']}"
                )
            else:
                value = f"{dumped['color_replace']['to_color']}_{dumped['color_replace']['tolerance']}"
            transforms.append(
                {
                    "cr": value,
                }
            )

        # -----------------------------
        # non-e transforms
        # -----------------------------
        if "blur" in dumped:
            transforms.append({"bl": dumped["blur"]})

        if "trim" in dumped:
            trim_params = dumped["trim"]
            if isinstance(trim_params, int):
                transforms.append({"t": trim_params})
            elif trim_params is True:
                transforms.append({"t": "true"})

        if "border" in dumped:
            border_params = dumped["border"]
            border_value = f"{border_params['border_width']}_{border_params['color']}"
            transforms.append({"b": border_value})

        if "rotate" in dumped:
            rotate_params = dumped["rotate"]
            transforms.append({"rt": rotate_params})

        if "flip" in dumped:
            flip_params = dumped["flip"]
            transforms.append({"fl": flip_params})

        if "radius" in dumped:
            radius_params = dumped["radius"]
            transforms.append({"r": radius_params})

        if "background" in dumped:
            bg = (
                self.background
                if isinstance(self.background, Background)
                else Background.from_raw(self.background)
            )
            transforms.append({"background": bg.to_ik_params()})

        if "opacity" in dumped:
            transforms.append({"o": dumped["opacity"]})

        return transforms


class EffectsAndEnhancementTransforms:
    """
    Wrapper around `Effects` to normalize parameters and emit the list of
    transformation dicts expected by the ImageKit URL builder.

    Public API:
        effects_and_enhancement(**params) -> List[Dict[str, Any]]
    """

    def effects_and_enhancement(self, **params: Any) -> List[Dict[str, Any]]:
        """
        Public entry point. Filters unsupported params and forwards the rest to
        `_effects_and_enhancement_impl`. Unknown keys are logged (debug) and
        ignored so callers can pass broader dictionaries without failing.
        """
        known_keys = Effects.model_fields.keys()
        known: dict[str, Any] = {}
        extra: dict[str, Any] = {}

        for k, v in params.items():
            if k in known_keys:
                known[k] = v
            else:
                extra[k] = v

        if extra:
            logger.debug("Ignoring unsupported effects params: %s", extra)

        return self._effects_and_enhancement_impl(**known)

    def _effects_and_enhancement_impl(
        self,
        contrast: Optional[bool] = None,
        sharpen: Optional[Union[bool, int]] = None,
        grayscale: Optional[bool] = None,
        unsharp_mask: Optional[Union[UnsharpMaskEffect, Dict[str, Any]]] = None,
        shadow: Optional[Union[bool, ShadowEffect, Dict[str, Any]]] = None,
        gradient: Optional[Union[bool, GradientEffect, Dict[str, Any]]] = None,
        perspective_distort: Optional[
            Union[PerspectiveDistortEffect, Dict[str, Any]]
        ] = None,
        arc_distort: Optional[Union[ArcDistortEffect, Dict[str, Any]]] = None,
        color_replace: Optional[Union[ColorReplaceEffect, Dict[str, Any]]] = None,
        border: Optional[Union[BorderEffect, Dict[str, Any]]] = None,
        blur: Optional[int] = None,
        trim: Optional[Union[Literal[True], int]] = None,
        rotate: Optional[Union[NumberOrExpression, Literal["auto"]]] = None,
        flip: Optional[FlipMode] = None,
        radius: Optional[Union[NumberOrExpression, Literal["max"]]] = None,
        background: Optional[Union[BackgroundValue, Background]] = None,
        opacity: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Build and validate **effects & enhancement transformations** for ImageKit.

        Schema:
            image_path?:str
            encoded?:bool
            width?,height?,aspect_ratio?:num|expr
            crop?:"force"|"at_max"|"at_least"
            crop_mode?:"extract"|"pad_resize"
            focus?:
                "face"|"center"|"top"|"bottom"|
                "left"|"right"|
                "top_left"|"top_right"|
                "bottom_left"|"bottom_right"
            zoom?:float
            x?,y?,xc?,yc?:num|expr
            layer_x?,layer_y?:num|expr
            layer_focus?:
                "center"|"top"|"bottom"|"left"|"right"|
                "top_left"|"top_right"|
                "bottom_left"|"bottom_right"
            background?:BackgroundValue|Background
            quality?:int
            dpr?:float|str
            layer_mode?:"displace"|"multiply"|"cutout"|"cutter"
            child?:ImageOverlay
            effects?:Effects

        This method accepts a validated subset of ImageKit-supported visual effects,
        normalizes them, and emits a **list of transformation dictionaries** that can
        be serialized into an ImageKit URL.

        Key characteristics:
        - Validation is handled by the `Effects` Pydantic model
        - Unknown parameters are ignored by the public wrapper
        - Output order matches ImageKit execution semantics
        - This method does NOT construct URLs

        Supported categories:
        - Image enhancement (contrast, sharpen, unsharp mask)
        - Color & tone manipulation
        - Blur, trim, border, and geometry transforms
        - Shadows, gradients, and distortion effects
        - Orientation and masking utilities

        Parameters
        ----------
        contrast : bool, optional
            Enables automatic contrast enhancement.

            Behavior:
            - When `True`, applies ImageKit's global contrast stretch
            - No tunable parameters
            - Can be chained with other effects

        sharpen : bool | int, optional
            Applies basic sharpening.

            Accepted forms:
            - `True` → default sharpen
            - Integer ≥ 0 → sharpen strength

            Notes:
            - Less precise than `unsharp_mask`
            - Excessive values may introduce artifacts

        grayscale : bool, optional
            Converts the image to grayscale.

            Behavior:
            - Fully removes color information
            - No configuration options

        unsharp_mask : UnsharpMaskEffect | dict, optional
            Applies advanced unsharp masking for high-quality sharpening.

            Required parameters:
            - `radius`   : positive float
            - `sigma`    : positive float
            - `amount`   : positive float
            - `threshold`: positive float

            Notes:
            - More computationally expensive than `sharpen`
            - All parameters must be provided together

        shadow : bool | ShadowEffect | dict, optional
            Adds a drop shadow beneath non-transparent pixels.

            Accepted forms:
            - `True` → default shadow
            - Configurable parameters:
                - `blur`        : 0–15
                - `saturation`  : 0–100
                - `x_offset`    : -100 to 100 (% of width)
                - `y_offset`    : -100 to 100 (% of height)

            Constraints:
            - Works only on images ≤ 2MP
            - Requires transparency to be visually meaningful
            - Negative offsets are supported

        gradient : bool | GradientEffect | dict, optional
            Applies a linear gradient overlay.

            Parameters:
            - `linear_direction` : angle (0–360) or positional keyword
            - `from_color`       : SVG color, RGB hex, or RGBA hex
            - `to_color`         : SVG color, RGB hex, or RGBA hex
            - `stop_point`       : float, pixel value, or arithmetic expression

            Defaults:
            - Direction: bottom (180)
            - From: white
            - To: transparent black

        perspective_distort : PerspectiveDistortEffect | dict, optional
            Applies perspective warp using 4 corner coordinates.

            Requirements:
            - All 8 values (`x1`–`y4`) are required
            - Coordinates are specified clockwise from top-left
            - Arithmetic expressions are not supported

        arc_distort : ArcDistortEffect | dict, optional
            Applies arc distortion to curve the image.

            Parameters:
            - `degrees`: positive or negative number

            Notes:
            - Negative values curve upward
            - Positive values curve downward

        color_replace : ColorReplaceEffect | dict, optional
            Replaces a source color and its similar shades.

            Parameters:
            - `to_color`   : required
            - `tolerance`  : 0–100 (default 35)
            - `from_color` : optional (auto-detected if omitted)

            Notes:
            - Best suited for saturated colors
            - High tolerance may affect unintended regions

        border : BorderEffect | dict, optional
            Adds a border around the image.

            Parameters:
            - `border_width` : number or arithmetic expression
            - `color`        : SVG color or hex

            Notes:
            - Border width is evaluated before rendering
            - Color alpha is not supported directly

        blur : int, optional
            Applies Gaussian blur.

            Constraints:
            - Integer values only
            - Range: 1–100
            - Higher values significantly increase blur radius

        trim : True | int, optional
            Trims solid or near-solid background pixels.

            Accepted forms:
            - `True` → default trim
            - Integer `1–99` → trim threshold

            Notes:
            - Best suited for uniform backgrounds
            - Higher values trim more aggressively

        rotate : NumberOrExpression | "auto", optional
            Rotates the image.

            Accepted forms:
            - Degrees (positive or negative)
            - `"auto"` → EXIF-based rotation
            - Arithmetic expressions

            Notes:
            - Rotation occurs after resizing

        flip : FlipMode, optional
            Mirrors the image.

            Supported values:
            - `"h"`   → horizontal
            - `"v"`   → vertical
            - `"h_v"` → both directions

        radius : NumberOrExpression | "max", optional
            Rounds image corners.

            Accepted forms:
            - Positive number
            - Arithmetic expression
            - `"max"` → fully circular mask

            Notes:
            - Applied after resizing
            - Must be chained after crop operations

        background:
            - For Solid color, requires hex, RGBA hex or svg color name
            - For dominant color background, use "dominant"
            - For blurred background use
                background: {"blur_intensity": Union[int] = "auto", brightness: [-255 to 255]}
            - For Gradient background use
                background: {"mode": "dominant", "pallete_size": Literal[2,4]=2}

        opacity : int, optional
            Sets overall image opacity.

            Constraints:
            - Integer `0–100`
            - Applied uniformly across the image

        Returns
        -------
        List[Dict[str, Any]]
            A list of normalized ImageKit transformation dictionaries,
            ordered and formatted for direct consumption by the URL builder.

            Example:
            [
                {"e": "contrast"},
                {"e-shadow": "bl-10_st-30_x-2_y-2"},
                {"r": 20}
            ]

        """
        effects = Effects(
            contrast=contrast,
            sharpen=sharpen,
            grayscale=grayscale,
            unsharp_mask=unsharp_mask,
            shadow=shadow,
            gradient=gradient,
            perspective_distort=perspective_distort,
            arc_distort=arc_distort,
            color_replace=color_replace,
            border=border,
            blur=blur,
            trim=trim,
            rotate=rotate,
            flip=flip,
            radius=radius,
            background=background,
            opacity=opacity,
        )

        return effects.to_transform_dicts()
