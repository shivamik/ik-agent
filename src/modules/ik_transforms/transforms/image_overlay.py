# TODO: Add examples for gradient as underlay
# TODO: Add example as
"""Image overlay transformation model for ImageKit."""

import logging
from typing import Optional, Union, Dict, Any, Literal
from pydantic import BaseModel, model_validator

from src.config import LOG_LEVEL
from src.modules.ik_transforms.types import (
    ImageLayerMode,
    BackgroundValue,
    NumberOrExpression,
    DisplacementMode,
    MultiplyMode,
    CutoutMode,
    CutterMode,
    Background,
)
from src.modules.ik_transforms.transforms.effects_and_enhancement import Effects

logger = logging.getLogger("transforms.image_overlay")
logger.setLevel(LOG_LEVEL)


class ImageOverlay(BaseModel):
    """
    Validated ImageKit image overlay specification.

    This model captures all supported layer parameters for placing an image
    overlay on a base asset. It is intended to be LLM-friendlayer_y: every field
    mirrors ImageKit's short transformation keys (`w`, `h`, `layer_x`, `layer_y`, etc.)
    while providing validation for common misuse:

    - Enforces exactlayer_y one image input (`image_path` or `image_path_encoded`).
    - Guards context-sensitive parameters (e.g., `z` onlayer_y with `fo="face"`,
      crop coordinates onlayer_y with `cm="extract"`, `dpr` onlayer_y when `w` or `h`
      is provided).
    - Supports a single nested overlay via the `child` field so complex
      compositions can be built recursivelayer_y.

    Example:
        ```python
        overlay = ImageOverlay(
            image_path="logo.png",
            w=200,
            h="bh_div_5",
            layer_x="bw_mul_0.05",
            layer_y="bh_mul_0.05",
            e_shadow=EShadow(),  # blur-10 saturation-30 offsets=2,2
        )
        spec = overlay.to_overlay_dict()
        # -> {"overlay": {"type": "image", "input": "logo.png", ...}}
        ```
    """

    # -------------------------------------------------
    # IMAGE SOURCE
    # -------------------------------------------------
    image_path: Optional[str] = None
    encoded: bool = False

    # -------------------------------------------------
    # SIZE & CROP
    # -------------------------------------------------
    width: Optional[NumberOrExpression] = None
    height: Optional[NumberOrExpression] = None
    aspect_ratio: Optional[NumberOrExpression] = None

    crop: Optional[Literal["force", "at_max", "at_least"]] = None
    crop_mode: Optional[Literal["extract", "pad_resize"]] = None
    focus: Optional[
        Literal[
            "face",
            "center",
            "top",
            "bottom",
            "left",
            "right",
            "top_left",
            "top_right",
            "bottom_left",
            "bottom_right",
        ]
    ] = None
    zoom: Optional[float] = None

    x: Optional[NumberOrExpression] = None
    y: Optional[NumberOrExpression] = None
    xc: Optional[NumberOrExpression] = None
    yc: Optional[NumberOrExpression] = None

    # -------------------------------------------------
    # POSITION
    # -------------------------------------------------
    layer_x: Optional[NumberOrExpression] = None
    layer_y: Optional[NumberOrExpression] = None
    layer_focus: Optional[
        Literal[
            "center",
            "top",
            "bottom",
            "left",
            "right",
            "top_left",
            "top_right",
            "bottom_left",
            "bottom_right",
        ]
    ] = None

    # -------------------------------------------------
    # APPEARANCE
    # -------------------------------------------------
    background: Optional[Union[BackgroundValue, Background]] = None
    quality: Optional[int] = None
    dpr: Optional[Union[float, str]] = None
    # -------------------------------------------------
    # NESTED OVERLAY (ONlayer_y ONE)
    # -------------------------------------------------
    layer_mode: Optional[Literal["displace", "multiply", "cutout", "cutter"]] = None
    child: Optional["ImageOverlay"] = None

    effects: Optional[Effects] = None

    def _resolve_layer_mode(self) -> Optional[ImageLayerMode]:
        if self.layer_mode is None:
            return None

        if self.layer_mode == "displace":
            if self.x is None and self.y is None:
                raise ValueError(
                    "Displacement layer mode requires at least one of x or y."
                )
            return DisplacementMode(x=self.x, y=self.y)

        if self.layer_mode == "multiply":
            return MultiplyMode()

        if self.layer_mode == "cutout":
            return CutoutMode()

        if self.layer_mode == "cutter":
            return CutterMode()

        # defensive (should never happen due to Literal)
        raise ValueError(f"Unknown layer mode: {self.layer_mode}")

    @model_validator(mode="after")
    def validate_image_source(self):
        if not self.image_path:
            raise ValueError("ImageOverlay requires image_path")

        if self.image_path == "ik_canvas":
            if self.width is None or self.height is None:
                raise ValueError(
                    "Solid color overlay requires width and height dimensions"
                )

            if self.background is None:
                raise ValueError(
                    "Solid color overlay requires background (background color)"
                )

        if self.zoom is not None and self.focus != "face":
            raise ValueError("zoom (zoom) requires focus='face'")

        if any(v is not None for v in (self.x, self.y, self.xc, self.yc)):
            if (self.crop_mode != "extract") and (self.layer_mode is None):
                raise ValueError(
                    "x/y/xc/yc require cm='extract' or layer_mode='displace'"
                )

        if self.dpr is not None and not (self.width or self.height):
            raise ValueError("dpr requires width or height")

        return self

    def to_overlay_dict(self) -> Dict[str, Any]:
        """
        Convert the overlay model into the nested dict structure expected by
        the ImageKit URL builder.

        Uses `model_dump()` to ensure all NumberOrExpression fields are
        serialized correctlayer_y (e.g. negative numbers -> 'N{abs(x)}').
        """
        dumped = self.model_dump(exclude_none=True)
        overlay: Dict[str, Any] = {
            "type": "image",
            "input": dumped["image_path"],
            "encoding": "plain" if not dumped.get("encoded") else "base64",
        }

        # -------------------------------------------------
        # POSITION
        # -------------------------------------------------
        position: Dict[str, Any] = {}

        if "layer_x" in dumped:
            position["x"] = dumped["layer_x"]

        if "layer_y" in dumped:
            position["y"] = dumped["layer_y"]

        if "layer_focus" in dumped:
            position["focus"] = dumped["layer_focus"]

        if position:
            overlay["position"] = position

        # -------------------------------------------------
        # TRANSFORMATIONS
        # -------------------------------------------------
        transform: Dict[str, Any] = {}
        # width
        if "width" in dumped:
            transform["width"] = dumped["width"]

        # height
        if "height" in dumped:
            transform["height"] = dumped["height"]

        # aspect_ratio
        if "aspect_ratio" in dumped:
            transform["aspect_ratio"] = dumped["aspect_ratio"]
        # crop
        if "crop" in dumped:
            transform["crop"] = dumped["crop"]

        # crop_mode
        if "crop_mode" in dumped:
            transform["crop_mode"] = dumped["crop_mode"]

        # focus
        if "focus" in dumped:
            transform["focus"] = dumped["focus"]

        # zoom
        if "zoom" in dumped:
            transform["zoom"] = dumped["zoom"]

        # x
        if "x" in dumped:
            transform["x"] = dumped["x"]
        # y
        if "y" in dumped:
            transform["y"] = dumped["y"]

        # xc
        if "xc" in dumped:
            transform["xc"] = dumped["xc"]
        # yc
        if "yc" in dumped:
            transform["yc"] = dumped["yc"]
        # background

        if "background" in dumped:
            bg = (
                self.background
                if isinstance(self.background, Background)
                else Background.from_raw(self.background)
            )
            transform["background"] = bg.to_ik_params()

        # quality
        if "quality" in dumped:
            transform["quality"] = dumped["quality"]
        # dpr
        if "dpr" in dumped:
            transform["dpr"] = dumped["dpr"]

        # -------------------------------------------------
        # EFFECTS
        # -------------------------------------------------
        if self.effects is not None:
            effects_transforms = self.effects.to_transform_dicts()
            for effect in effects_transforms:
                transform.update(effect)
            # print("effects_transforms:", effects_transforms)

        # -------------------------------------------------
        # NESTED OVERLAY
        # -------------------------------------------------
        if self.child is not None:
            child_overlay = self.child.to_overlay_dict()
            if child_overlay:
                transform["overlay"] = child_overlay["overlay"]

        layer_mode_obj = self._resolve_layer_mode()
        if layer_mode_obj:
            transform.update(layer_mode_obj.to_ik_params())

        if transform:
            overlay["transformation"] = [transform]

        return {"overlay": overlay}


class ImageOverlayTransforms:
    """
    Wrapper around `ImageOverlay` to normalize overlay parameters and emit the
    minimal dict expected by the ImageKit URL builder.

    Public API:
        image_overlay(**params) -> Dict[str, Any]

    This mirrors the ergonomic pattern used in `AITransforms`: a public wrapper
    filters unknown arguments, while `_image_overlay_impl` exposes a clear,
    typed signature for LLMs and human callers. Validation is delegated to the
    Pydantic `ImageOverlay` model, which enforces source selection, positional
    constraints, effect compatibility, and nested overlay composition.
    """

    def image_overlay(self, **params: Any) -> Dict[str, Any]:
        """
        Public entry point. Filters unsupported params and forwards the rest to
        `_image_overlay_impl`. Unknown keys are logged (debug) and ignored so
        callers can pass broader dictionaries without failing.
        """
        known_keys = ImageOverlay.model_fields.keys()

        known: dict[str, Any] = {}
        extra: dict[str, Any] = {}

        for k, v in params.items():
            if k in known_keys:
                known[k] = v
            else:
                extra[k] = v

        if extra:
            logger.debug("Ignoring unsupported overlay params: %s", extra)

        return self._image_overlay_impl(**known)

    def _image_overlay_impl(
        self,
        image_path: Optional[str] = None,
        encoded: bool = False,
        w: Optional[NumberOrExpression] = None,
        h: Optional[NumberOrExpression] = None,
        ar: Optional[NumberOrExpression] = None,
        c: Optional[Literal["force", "at_max", "at_least"]] = None,
        cm: Optional[Literal["extract", "pad_resize"]] = None,
        fo: Optional[
            Literal[
                "face",
                "center",
                "top",
                "bottom",
                "left",
                "right",
                "top_left",
                "top_right",
                "bottom_left",
                "bottom_right",
            ]
        ] = None,
        z: Optional[NumberOrExpression] = None,
        x: Optional[NumberOrExpression] = None,
        y: Optional[NumberOrExpression] = None,
        xc: Optional[NumberOrExpression] = None,
        yc: Optional[NumberOrExpression] = None,
        layer_x: Optional[NumberOrExpression] = None,
        layer_y: Optional[NumberOrExpression] = None,
        layer_focus: Optional[str] = None,
        q: Optional[int] = None,
        dpr: Optional[Union[float, str]] = None,
        layer_mode: Optional[
            Literal["displace", "multiply", "cutout", "cutter"]
        ] = None,
        child: Optional[dict] = None,
        effects: Optional[Effects] = None,
    ) -> Dict[str, Any]:
        """
        Build and normalize an ImageKit **image overlay** into a single overlay
        transformation dictionary.

        Use this docstring as a **ground-truth parameter map** when prompting
        an LLM: all constraints, coupling rules, and defaults are documented here.

        Note: This transform can add image or solid color overlays to a base image.
        For Solid Color overlays, use `image_path="ik_canvas"` and specify
        dimensions via `w` and `h` and `bg` for color.
        -------------------------------------------------------------------------
        IMAGE SOURCE (exactlayer_y one required)
        -------------------------------------------------------------------------
        image_path:
            Plain ImageKit media library path for the overlay image or
            use ik_canvas for solid Color overlays
            Example: `"logo.png"` or `ik_canvas`

        encoded:
            a flag to specify if we need to encode image_path to base64 or not.

        -------------------------------------------------------------------------
        SIZE, CROP & FOCUS (applied to the overlay image itself)
        -------------------------------------------------------------------------
        w:
            Output width of the overlay image. Accepts numbers or arithmetic
            expressions (e.g. `"bw_div_2"`).

        h:
            Output height of the overlay image. Accepts numbers or arithmetic
            expressions (e.g. `"bh_mul_0.5"`).

        ar:
            Aspect ratio of the overlay image. Can be numeric or an arithmetic
            expression (e.g. `"16-9"` or `"iar_div_2"`).

        c:
            Crop strategy. One of:
            - `"force"`: force resize, ignore aspect ratio
            - `"at_max"`: resize until max constraint
            - `"at_least"`: resize until minimum constraint

        cm:
            Crop mode controlling extraction or padding.
            - `"extract"`: crop from the image
            - `"pad_resize"`: resize and pad with background

        fo:
            Focus area for cropping.
            Supports relative anchors (`center`, `top_left`, etc.) and
            intelligent options like `"face"`.

        z:
            Zoom factor for object/face-aware cropping.
            **Onlayer_y valid when `fo="face"`**.
            Values < 1 zoom out, values > 1 zoom in.

        x, y:
            Top-left crop coordinates.
            **Onlayer_y valid when `cm="extract"`**.

        xc, yc:
            Center-based crop coordinates.
            **Onlayer_y valid when `cm="extract"`**.

        -------------------------------------------------------------------------
        LAYER POSITIONING (relative to base image)
        -------------------------------------------------------------------------
        layer_x:
            X-axis position of the overlay layer.
            Supports negative values and arithmetic expressions.

        layer_y:
            Y-axis position of the overlay layer.
            Supports negative values and arithmetic expressions.

        layer_focus:
            Relative layer focus anchor.
            Examples: `"top_left"`, `"center"`, `"bottom_right"`.

        -------------------------------------------------------------------------
        APPEARANCE & OUTPUT TUNING
        -------------------------------------------------------------------------
        background:
            - For Solid color, requires hex, RGBA hex or svg color name
            - For dominant color background, use "dominant"
            - For blurred background use
                background: {"blur_intensity": Union[int] = "auto", brightness: [-255 to 255]}
            - For Gradient background use
                background: {"mode": "dominant", "pallete_size": Literal[2,4]=2}

        q:
            Output quality for lossy formats (1–100).

        dpr:
            Device pixel ratio (`0.1–5` or `"auto"`).
            **Requires at least one of `w` or `h`.**

        -------------------------------------------------------------------------
        EFFECTS (applied to the overlay image)
        -------------------------------------------------------------------------
        effects:
            Effects instance capturing enhancement and filter effects

            effects: dict = {
                "contrast": bool,
                "grayscale": bool,
                "sharpen": bool | int,
                "unsharp_mask": {
                    "radius": float,      # > 0
                    "sigma": float,       # > 0
                    "amount": float,      # > 0
                    "threshold": float    # > 0
                },
                "shadow": true | {
                    "blur": int,          # 0–15 (default: 10)
                    "saturation": int,    # 0–100 (default: 30)
                    "x_offset": number | expression,  # default: 2
                    "y_offset": number | expression   # default: 2
                },
                "gradient": true | {
                    "linear_direction": int | POSITION,   # 0–360 (default: 180)
                    "from_color": Color,                  # default: "FFFFFF"
                    "to_color": Color,                    # default: "00000000"
                    "stop_point": float | expression      # default: 1
                },
                "perspective_distort": {
                    "x1": number, "y1": number,
                    "x2": number, "y2": number,
                    "x3": number, "y3": number,
                    "x4": number, "y4": number
                },
                "arc_distort": {
                    "degrees": number
                },
                "color_replace": {
                    "to_color": Color,
                    "tolerance": int,      # 0–100 (default: 35)
                    "from_color": Color | None
                },
                "border": {
                    "border_width": number | expression,
                    "color": Color
                },
                "blur": int,             # 1–100
                "trim": true | int,
                "rotate": number | expression | "auto",
                "flip": "h" | "v" | "h_v",
                "radius": number | expression | "max",
                "background": Color | "dominant" | Background,
                "opacity": int           # 0–100
            }


        -------------------------------------------------------------------------
        NESTING
        -------------------------------------------------------------------------

        child:
            Optional **single nested overlay**.
            The child overlay is embedded under
            `transformation.overlay` to build layered compositions.
            (Onlayer_y one child is supported here by design.)

        -------------------------------------------------------------------------
        RETURNS
        -------------------------------------------------------------------------
        Dict[str, Any]:
            A normalized ImageKit overlay dictionary ready to be
            appended to a transformation chain.

            If `enabled` is False, returns `{}`.
        """
        if child is not None:
            child = ImageOverlay(**child)

        overlay = ImageOverlay(
            image_path=image_path,
            encoded=encoded,
            w=w,
            h=h,
            ar=ar,
            c=c,
            cm=cm,
            fo=fo,
            z=z,
            x=x,
            y=y,
            xc=xc,
            yc=yc,
            layer_x=layer_x,
            layer_y=layer_y,
            layer_focus=layer_focus,
            q=q,
            dpr=dpr,
            layer_mode=layer_mode,
            child=child,
        )

        return overlay.to_overlay_dict()
