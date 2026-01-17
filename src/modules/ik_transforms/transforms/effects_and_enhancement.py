"""
transforms.py

Validated Effects & Enhancements transformation model for ImageKit.

This module:
- Validates effect parameters
- Normalizes them into ImageKit-compatible transformation dicts
- Does NOT build URLs
"""

from typing import Optional, Dict, Any, Literal, List, Union
from pydantic import BaseModel, Field, model_validator, field_validator

from ..types import (
    NumberOrExpression,
    POSITION,
    Color,
    Number,
    FlipMode,
    BACKGROUND,
    BlurredBackground,
    GradientBackground,
)

# -------------------------------------------------------------------
# Effect sub-models
# -------------------------------------------------------------------


class UnsharpMaskEffect(BaseModel):
    radius: float = Field(..., gt=0)
    sigma: float = Field(..., gt=0)
    amount: float = Field(..., gt=0)
    threshold: float = Field(..., gt=0)


class ShadowEffect(BaseModel):
    # e-shadow-<blur>_<saturation>_<x-offset>_<y-offset>
    blur: int = Field(10, ge=0, le=15)
    saturation: int = Field(30, ge=0, le=100)
    x_offset: NumberOrExpression = 2
    y_offset: NumberOrExpression = 2


class GradientEffect(BaseModel):
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
    x1: NumberOrExpression
    y1: NumberOrExpression
    x2: NumberOrExpression
    y2: NumberOrExpression
    x3: NumberOrExpression
    y3: NumberOrExpression
    x4: NumberOrExpression
    y4: NumberOrExpression


class ArcDistortEffect(BaseModel):
    degrees: Number


class BorderEffect(BaseModel):
    border_width: NumberOrExpression
    color: Color


class ColorReplaceEffect(BaseModel):
    to_color: Color
    tolerance: int = Field(35, ge=0, le=100)
    from_color: Optional[Color] = None


# -------------------------------------------------------------------
# Main Effects class
# -------------------------------------------------------------------


class Effects(BaseModel):
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
    background: Optional[BACKGROUND] = None
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
        Returns a list of ImageKit transformation dicts.
        """
        transforms: list[Dict[str, Any]] = []
        dumped = self.model_dump(exclude_none=True)
        # effects: List[Dict[str, Any]] = []

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
            transforms["bl"] = dumped["blur"]

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
            # print("background", dumped["background"])
            background_value = dumped["background"]
            if isinstance(self.background, Color):
                transforms.append({"bg": background_value})
            elif self.background == "dominant":
                transforms.append({"bg": background_value})
            elif isinstance(self.background, BlurredBackground):
                value = f"blurred_{self.background.blur_intensity}_{self.background.brightness}"
                transforms.append({"bg": value})
            elif isinstance(self.background, GradientBackground):
                value = (
                    f"gradient_{self.background.mode}_{self.background.pallete_size}"
                )
                transforms.append({"bg": background_value})
            # transforms["bg"] =

        if "opacity" in dumped:
            transforms.append({"o": dumped["opacity"]})

        return transforms
