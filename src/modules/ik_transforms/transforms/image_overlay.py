"""Image overlay transformation model for ImageKit."""

import logging
from typing import Optional, Union, Dict, Any, Literal
from pydantic import BaseModel, model_validator

from src.config import LOG_LEVEL
from src.modules.ik_transforms.types import (
    NumberOrExpression,
    EUSM,
    EShadow,
    EGradient,
    EDistort,
)

logger = logging.getLogger("transforms.image_overlay")
logger.setLevel(LOG_LEVEL)


class ImageOverlay(BaseModel):
    """
    Validated ImageKit image overlay specification.

    This model captures all supported layer parameters for placing an image
    overlay on a base asset. It is intended to be LLM-friendly: every field
    mirrors ImageKit's short transformation keys (`w`, `h`, `lx`, `ly`, etc.)
    while providing validation for common misuse:

    - Enforces exactly one image input (`image_path` or `image_path_encoded`).
    - Guards context-sensitive parameters (e.g., `z` only with `fo="face"`,
      crop coordinates only with `cm="extract"`, `dpr` only when `w` or `h`
      is provided).
    - Supports a single nested overlay via the `child` field so complex
      compositions can be built recursively.

    Example:
        ```python
        overlay = ImageOverlay(
            image_path="logo.png",
            w=200,
            h="bh_div_5",
            lx="bw_mul_0.05",
            ly="bh_mul_0.05",
            e_shadow=EShadow(),  # blur-10 saturation-30 offsets=2,2
        )
        spec = overlay.to_overlay_dict()
        # -> {"overlay": {"type": "image", "input": "logo.png", ...}}
        ```
    """

    _TRANSFORM_ATTRS = (
        "w",
        "h",
        "ar",
        "c",
        "cm",
        "fo",
        "z",
        "x",
        "y",
        "xc",
        "yc",
        "bg",
        "b",
        "o",
        "r",
        "rt",
        "fl",
        "q",
        "bl",
        "dpr",
        "t",
    )

    # -------------------------------------------------
    # IMAGE SOURCE
    # -------------------------------------------------
    image_path: Optional[str] = None
    encoded: bool = False

    # -------------------------------------------------
    # SIZE & CROP
    # -------------------------------------------------
    w: Optional[NumberOrExpression] = None
    h: Optional[NumberOrExpression] = None
    ar: Optional[NumberOrExpression] = None

    c: Optional[Literal["force", "at_max", "at_least"]] = None
    cm: Optional[Literal["extract", "pad_resize"]] = None
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
    ] = None
    z: Optional[NumberOrExpression] = None

    x: Optional[NumberOrExpression] = None
    y: Optional[NumberOrExpression] = None
    xc: Optional[NumberOrExpression] = None
    yc: Optional[NumberOrExpression] = None

    # -------------------------------------------------
    # POSITION
    # -------------------------------------------------
    lx: Optional[NumberOrExpression] = None
    ly: Optional[NumberOrExpression] = None
    lfo: Optional[
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
    bg: Optional[str] = None
    b: Optional[str] = None
    o: Optional[int] = None
    r: Optional[Union[int, str]] = None
    rt: Optional[int] = None
    fl: Optional[str] = None
    q: Optional[int] = None
    bl: Optional[int] = None
    dpr: Optional[Union[float, str]] = None
    t: Optional[Union[bool, int]] = None

    # -------------------------------------------------
    # EFFECTS
    # -------------------------------------------------
    e_grayscale: bool = False
    e_contrast: bool = False
    e_sharpen: Union[bool, int] = False
    e_usm: Union[EUSM, bool] = False
    e_shadow: Union[EShadow, bool] = False
    e_gradient: Union[EGradient, bool] = False
    e_distort: Union[EDistort, bool] = False

    # -------------------------------------------------
    # NESTED OVERLAY (ONLY ONE)
    # -------------------------------------------------
    child: Optional["ImageOverlay"] = None

    @model_validator(mode="after")
    def validate_image_source(self):
        if not self.image_path:
            raise ValueError("ImageOverlay requires image_path")

        if self.image_path == "ik_canvas":
            if self.w is None or self.h is None:
                raise ValueError("Solid color overlay requires w and h dimensions")

            # if self.lx is None or self.ly is None:
            #     raise ValueError("Solid color overlay requires lx and ly positioning")

            if self.bg is None:
                raise ValueError("Solid color overlay requires bg (background color)")

        if self.z is not None and self.fo != "face":
            raise ValueError("z (zoom) requires fo='face'")

        if any(v is not None for v in (self.x, self.y, self.xc, self.yc)):
            if self.cm != "extract":
                raise ValueError("x/y/xc/yc require cm='extract'")

        if self.dpr is not None and not (self.w or self.h):
            raise ValueError("dpr requires w or h")

        if self.e_grayscale and self.e_contrast:
            raise ValueError("Use either e_grayscale or e_contrast, not both")

        return self

    def _build_transform_dict(self) -> Dict[str, Any]:
        """Collect transformation parameters into ImageKit's short-key dict."""
        transform: Dict[str, Any] = {}

        for attr in self._TRANSFORM_ATTRS:
            val = getattr(self, attr)
            if val is not None:
                transform[attr] = val

        if self.e_grayscale:
            transform["e"] = "grayscale"
        if self.e_contrast:
            transform["e"] = "contrast"

        if self.e_sharpen:
            transform["e-sharpen"] = (
                self.e_sharpen if isinstance(self.e_sharpen, int) else None
            )

        if isinstance(self.e_usm, EUSM):
            transform["e-usm"] = (
                f"{self.e_usm.radius}-{self.e_usm.sigma}-"
                f"{self.e_usm.amount}-{self.e_usm.threshold}"
            )

        if isinstance(self.e_shadow, EShadow):
            transform["e-shadow"] = (
                f"{self.e_shadow.blur}-{self.e_shadow.saturation}-"
                f"{self.e_shadow.x_offset}-{self.e_shadow.y_offset}"
            )

        if isinstance(self.e_gradient, EGradient):
            transform["e-gradient"] = (
                f"ld-{self.e_gradient.linear_direction}_"
                f"from-{self.e_gradient.from_color}_"
                f"to-{self.e_gradient.to_color}_"
                f"sp-{self.e_gradient.stop_point}"
            )

        if isinstance(self.e_distort, EDistort):
            if self.e_distort.type == "perspective":
                transform["e-distort"] = (
                    f"p-{self.e_distort.x1}_{self.e_distort.y1}_"
                    f"{self.e_distort.x2}_{self.e_distort.y2}_"
                    f"{self.e_distort.x3}_{self.e_distort.y3}_"
                    f"{self.e_distort.x4}_{self.e_distort.y4}"
                )
            else:
                transform["e-distort"] = f"a-{self.e_distort.arc_degree}"

        return transform

    def to_overlay_dict(self) -> Dict[str, Any]:
        """
        Convert the overlay model into the nested dict structure expected by
        the ImageKit URL builder.

        Uses `model_dump()` to ensure all NumberOrExpression fields are
        serialized correctly (e.g. negative numbers -> 'N{abs(x)}').
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

        if "lx" in dumped:
            position["x"] = dumped["lx"]

        if "ly" in dumped:
            position["y"] = dumped["ly"]

        if "lfo" in dumped:
            position["focus"] = dumped["lfo"]

        if position:
            overlay["position"] = position

        # -------------------------------------------------
        # TRANSFORMATIONS
        # -------------------------------------------------
        transform: Dict[str, Any] = {}

        for attr in self._TRANSFORM_ATTRS:
            if attr in dumped:
                transform[attr] = dumped[attr]

        # effects
        if dumped.get("e_grayscale"):
            transform["e"] = "grayscale"

        if dumped.get("e_contrast"):
            transform["e"] = "contrast"

        if isinstance(self.e_sharpen, int):
            transform["e-sharpen"] = self.e_sharpen
        elif dumped.get("e_sharpen") is True:
            transform["e-sharpen"] = None

        if isinstance(self.e_usm, EUSM):
            transform["e-usm"] = (
                f"{self.e_usm.radius}-{self.e_usm.sigma}-"
                f"{self.e_usm.amount}-{self.e_usm.threshold}"
            )

        if isinstance(self.e_shadow, EShadow):
            transform["e-shadow"] = (
                f"{self.e_shadow.blur}-{self.e_shadow.saturation}-"
                f"{self.e_shadow.x_offset}-{self.e_shadow.y_offset}"
            )

        if isinstance(self.e_gradient, EGradient):
            transform["e-gradient"] = (
                f"ld-{self.e_gradient.linear_direction}_"
                f"from-{self.e_gradient.from_color}_"
                f"to-{self.e_gradient.to_color}_"
                f"sp-{self.e_gradient.stop_point}"
            )

        if isinstance(self.e_distort, EDistort):
            if self.e_distort.type == "perspective":
                transform["e-distort"] = (
                    f"p-{dumped['e_distort']['x1']}_{dumped['e_distort']['y1']}_"
                    f"{dumped['e_distort']['x2']}_{dumped['e_distort']['y2']}_"
                    f"{dumped['e_distort']['x3']}_{dumped['e_distort']['y3']}_"
                    f"{dumped['e_distort']['x4']}_{dumped['e_distort']['y4']}"
                )
            else:
                transform["e-distort"] = f"a-{self.e_distort.arc_degree}"

        # -------------------------------------------------
        # NESTED OVERLAY
        # -------------------------------------------------
        if self.child is not None:
            child_overlay = self.child.to_overlay_dict()
            if child_overlay:
                transform["overlay"] = child_overlay["overlay"]

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
        lx: Optional[NumberOrExpression] = None,
        ly: Optional[NumberOrExpression] = None,
        lfo: Optional[str] = None,
        bg: Optional[str] = None,
        b: Optional[str] = None,
        o: Optional[int] = None,
        r: Optional[Union[int, str]] = None,
        rt: Optional[int] = None,
        fl: Optional[str] = None,
        q: Optional[int] = None,
        bl: Optional[int] = None,
        dpr: Optional[Union[float, str]] = None,
        t: Optional[Union[bool, int]] = None,
        e_grayscale: bool = False,
        e_contrast: bool = False,
        e_sharpen: Union[bool, int] = False,
        e_usm: Union[EUSM, bool] = False,
        e_shadow: Union[EShadow, bool] = False,
        e_gradient: Union[EGradient, bool] = False,
        e_distort: Union[EDistort, bool] = False,
        child: Optional[dict] = None,
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
        IMAGE SOURCE (exactly one required)
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
            **Only valid when `fo="face"`**.
            Values < 1 zoom out, values > 1 zoom in.

        x, y:
            Top-left crop coordinates.
            **Only valid when `cm="extract"`**.

        xc, yc:
            Center-based crop coordinates.
            **Only valid when `cm="extract"`**.

        -------------------------------------------------------------------------
        LAYER POSITIONING (relative to base image)
        -------------------------------------------------------------------------
        lx:
            X-axis position of the overlay layer.
            Supports negative values and arithmetic expressions.

        ly:
            Y-axis position of the overlay layer.
            Supports negative values and arithmetic expressions.

        lfo:
            Relative layer focus anchor.
            Examples: `"top_left"`, `"center"`, `"bottom_right"`.

        -------------------------------------------------------------------------
        APPEARANCE & OUTPUT TUNING
        -------------------------------------------------------------------------
        bg:
            Background color for padded areas.
            Accepts hex, RGBA, or color names.

        b:
            Border specification.
            Format: `"width_color"` (e.g. `"10_red"`).

        o:
            Opacity of the overlay image (0–100).

        r:
            Corner radius. Use `"max"` for circular/oval shapes.

        rt:
            Rotation in degrees.

        fl:
            Flip/mirror mode (horizontal, vertical, or both).

        q:
            Output quality for lossy formats (1–100).

        bl:
            Gaussian blur radius (1–100).

        dpr:
            Device pixel ratio (`0.1–5` or `"auto"`).
            **Requires at least one of `w` or `h`.**

        t:
            Trim behavior.
            - `True`: default trimming
            - `False`: disable trimming
            - `1–99`: trim threshold

        -------------------------------------------------------------------------
        EFFECTS (applied to the overlay image)
        -------------------------------------------------------------------------
        e_grayscale:
            Convert the overlay image to grayscale.

        e_contrast:
            Automatically enhance contrast.

        e_sharpen:
            Sharpen the image.
            - `True`: default sharpening
            - `int`: custom sharpening strength

        e_usm:
            Unsharp mask configuration.
            Accepts an `EUSM` model or `True` for default behavior.

        e_shadow:
            Drop shadow effect.
            Accepts an `EShadow` model or `True`.

        e_gradient:
            Linear gradient overlay.
            Accepts an `EGradient` model or `True`.

        e_distort:
            Distortion effect.
            Accepts an `EDistort` model for perspective or arc distortion.

        -------------------------------------------------------------------------
        NESTING
        -------------------------------------------------------------------------

        child:
            Optional **single nested overlay**.
            The child overlay is embedded under
            `transformation.overlay` to build layered compositions.
            (Only one child is supported here by design.)

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
            lx=lx,
            ly=ly,
            lfo=lfo,
            bg=bg,
            b=b,
            o=o,
            r=r,
            rt=rt,
            fl=fl,
            q=q,
            bl=bl,
            dpr=dpr,
            t=t,
            e_grayscale=e_grayscale,
            e_contrast=e_contrast,
            e_sharpen=e_sharpen,
            e_usm=e_usm,
            e_shadow=e_shadow,
            e_gradient=e_gradient,
            e_distort=e_distort,
            child=child,
        )

        return overlay.to_overlay_dict()
