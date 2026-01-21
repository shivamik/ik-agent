import logging
from typing import Any, Dict, Optional, Literal, Union

from pydantic import BaseModel, field_validator

from src.config import LOG_LEVEL
from src.modules.ik_transforms.types import (
    FONT_FAMILY,
    FONT_FILE_REGEX,
    FlipMode,
    TextLayerMode,
    InnerAlignment,
    BackgroundValue,
    NumberOrExpression,
    PaddingValue,
    AlphaLevel,
    CutoutMode,
    CutterMode,
    MultiplyMode,
    Background,
    Color,
)
from src.utils.tool_utils import list_assets

logger = logging.getLogger("transforms.text_overlay")
logger.setLevel(LOG_LEVEL)


class TextOverlay(BaseModel):
    text: str
    layer_x: Optional[NumberOrExpression] = None
    layer_y: Optional[NumberOrExpression] = None
    width: Optional[NumberOrExpression] = None
    font_size: Optional[NumberOrExpression] = None
    font_family: Optional[str] = None
    color: Optional[Color] = None
    inner_alignment: Optional[InnerAlignment] = None
    padding: Optional[PaddingValue] = None
    alpha: Optional[AlphaLevel] = None
    typography: Optional[
        Literal[
            "b",
            "i",
            "strikethrough",
            "b_i",
            "b_strikethrough",
            "i_strikethrough",
            "b_i_strikethrough",
        ]
    ] = None
    background: Optional[Union[BackgroundValue, Background]] = None
    corner_radius: Optional[NumberOrExpression] = None
    rotation: Optional[NumberOrExpression] = None
    flip: Optional[FlipMode] = None
    line_height: Optional[NumberOrExpression] = None
    layer_mode: Optional[Literal["multiply", "cutout", "cutter"]] = None

    @field_validator("font_family")
    @classmethod
    def validate_font_family(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v

        # Case 1: Standard ImageKit font
        if v in FONT_FAMILY:
            return v

        # Case 2: Custom font file path
        if FONT_FILE_REGEX.fullmatch(v):
            return v

        raise ValueError(
            f"Invalid font_family '{v}'. "
            "Must be a supported ImageKit font name or "
            "a valid custom font file path (e.g. fonts@@MyFont.ttf)."
        )

    @staticmethod
    async def ensure_font_exists(font_path: str):
        files = await list_assets(search_query=f'name="{font_path}"', limit=1)
        if not files:
            raise ValueError(f"Font file '{font_path}' not found")

    def _resolve_layer_mode(self) -> Optional[TextLayerMode]:
        if self.layer_mode is None:
            return None

        if self.layer_mode == "multiply":
            return MultiplyMode()

        if self.layer_mode == "cutout":
            return CutoutMode()

        if self.layer_mode == "cutter":
            return CutterMode()

        # defensive (should never happen due to Literal)
        raise ValueError(f"Unknown layer mode: {self.layer_mode}")

    async def to_overlay_dict(self) -> Dict[str, Any]:
        """
        Convert the overlay model into the nested dict structure expected by
        the ImageKit URL builder.

        Uses `model_dump()` to ensure all NumberOrExpression fields are
        serialized correctly (e.g. negative numbers -> 'N{abs(x)}').
        """
        dumped = self.model_dump(exclude_none=True)

        overlay: Dict[str, Any] = {"type": "text", "text": dumped["text"]}

        # -------------------------------------------------
        # POSITION
        # -------------------------------------------------
        position: Dict[str, Any] = {}

        if "layer_x" in dumped:
            position["x"] = dumped["layer_x"]

        if "ly" in dumped:
            position["y"] = dumped["layer_y"]

        if position:
            overlay["position"] = position

        # -------------------------------------------------
        # TRANSFORMATIONS
        # -------------------------------------------------
        transform: Dict[str, Any] = {}

        if "width" in dumped:
            transform["width"] = dumped["width"]

        if "font_size" in dumped:
            transform["font_size"] = dumped["font_size"]

        if "font_family" in dumped:
            if dumped["font_family"] not in FONT_FAMILY:
                await self.ensure_font_exists(dumped["font_family"])
            transform["font_family"] = dumped["font_family"]

        if "color" in dumped:
            transform["font_color"] = dumped["color"]

        if "typography" in dumped:
            overlay["typography"] = dumped["typography"]

        if "inner_alignment" in dumped:
            transform["inner_alignment"] = dumped["inner_alignment"]

        if "alpha" in dumped:
            transform["alpha"] = dumped["alpha"]

        if "padding" in dumped:
            transform["padding"] = dumped["padding"]

        if "background" in dumped:
            bg = (
                self.background
                if isinstance(self.background, Background)
                else Background.from_raw(self.background)
            )
            transform["background"] = bg.to_ik_params()

        if "corner_radius" in dumped:
            transform["radius"] = dumped["corner_radius"]

        if "rotation" in dumped:
            transform["rotation"] = dumped["rotation"]

        if "flip" in dumped:
            transform["flip"] = dumped["flip"]

        if "line_height" in dumped:
            transform["line_height"] = dumped["line_height"]

        layer_mode_obj = self._resolve_layer_mode()
        if layer_mode_obj:
            transform.update(layer_mode_obj.to_ik_params())

        if transform:
            overlay["transformation"] = [transform]

        return {"overlay": overlay}


class TextOverlayTransforms:
    """Wrapper that mirrors ImageOverlayTransforms for text overlays."""

    async def text_overlay(self, **params: Any) -> Dict[str, Any]:
        """
        Public entry point that filters unsupported parameters and forwards the
        rest to `_text_overlay_impl`.
        """
        known_keys = TextOverlay.model_fields.keys()

        known: dict[str, Any] = {}
        extra: dict[str, Any] = {}

        for k, v in params.items():
            if k in known_keys:
                known[k] = v
            else:
                extra[k] = v

        if extra:
            logger.debug("Ignoring unsupported overlay params: %s", extra)

        return await self._text_overlay_impl(**known)

    async def _text_overlay_impl(
        self,
        text: str,
        layer_x: Optional[NumberOrExpression] = None,
        layer_y: Optional[NumberOrExpression] = None,
        width: Optional[NumberOrExpression] = None,
        font_size: Optional[NumberOrExpression] = None,
        font_family: Optional[str] = None,
        color: Optional[str] = None,
        inner_alignment: Optional[Literal["left", "center", "right"]] = None,
        padding: Optional[PaddingValue] = None,
        alpha: Optional[AlphaLevel] = None,
        typography: Optional[
            Literal[
                "b",
                "i",
                "strikethrough",
                "b_i",
                "b_strikethrough",
                "i_strikethrough",
                "b_i_strikethrough",
            ]
        ] = None,
        background: Optional[str] = None,
        corner_radius: Optional[NumberOrExpression] = None,
        rotation: Optional[NumberOrExpression] = None,
        flip: Optional[FlipMode] = None,
        line_height: Optional[NumberOrExpression] = None,
        layer_mode: Optional[Literal["multiply", "cutout", "cutter"]] = None,
    ) -> Dict[str, Any]:
        """
        Build and validate a **text overlay layer** for ImageKit image transformations.

        Schema:
            text: string (required)
            layer_x?: number | expression
            layer_y?: number | expression
            width?: number | expression
            font_size?: number | expression
            font_family?: string
            color?: Color
            inner_alignment?: InnerAlignment
            padding?: PaddingValue
            alpha?: AlphaLevel
            typography?:
                "b" |
                "i" |
                "strikethrough" |
                "b_i" |
                "b_strikethrough" |
                "i_strikethrough" |
                "b_i_strikethrough"
            background?: BackgroundValue | Background
            corner_radius?: number | expression
            rotation?: number | expression
            flip?: "h" | "v" | "h_v"
            line_height?: number | expression
            layer_mode?:
                "multiply" | "cutout" | "cutter"

        Parameters
        ----------
        text : str
            The text content to overlay on the base image.

            Encoding rules (handled implicitly by the URL builder):
            - If the text contains only alphanumeric characters, "@", "-", or "_",
            it is emitted using the `i-` parameter.
            - Otherwise, the text must be base64-encoded and percent-encoded and
            emitted using the `ie-` parameter.

            ImageKit limits:
            - Plain text input is truncated after 2000 characters.
            - Base64-encoded input is truncated after 2500 characters.

        layer_x : NumberOrExpression, optional
            Horizontal position of the text layer relative to the base image.

            Accepted forms:
            - Positive or negative numbers
            - Arithmetic expressions (e.g. `bw_mul_0.1`, `bw_div_2`)

            If omitted, the text is horizontally centered.

        layer_y : NumberOrExpression, optional
            Vertical position of the text layer relative to the base image.

            Same rules as `layer_x` apply.
            If omitted, the text is vertically centered.

        width : NumberOrExpression, optional
            Maximum width (in pixels) of the text box.

            If the text exceeds this width, it is wrapped automatically.
            Accepts arithmetic expressions relative to base dimensions.

        font_size : NumberOrExpression, optional
            Font size of the text in points.

            Can be a fixed number or an arithmetic expression (e.g. `bw_mul_0.05`).

        font_family : str, optional
            Font family to use for rendering the text.

            Accepted values:
            - One of ImageKit's built-in fonts (e.g. `"Lato"`, `"Roboto"`)
            - A custom font file path (e.g. `"fonts/Poppins-Regular.ttf"` or
            `"fonts@@Poppins-Regular.ttf"`)

            If a custom font path is provided, its existence in the ImageKit media
            library is verified asynchronously before generating the overlay.

        color : str, optional
            Text color.

            Accepted formats:
            - RGB hex (e.g. `"FF0000"`)
            - RGBA hex with opacity suffix (e.g. `"FFAABB50"`)
            - Named colors (e.g. `"red"`)

        inner_alignment : {"left", "center", "right"}, optional
            Horizontal alignment of text within the text box.
            Defaults to `"center"` if omitted.

        padding : PaddingValue, optional
            Padding around the text box.

            Accepted forms:
            - Single positive integer (uniform padding)
            - CSS-style shorthand (`top_right_bottom_left`) using underscores
            (e.g. `10_20_30_40`)
            - Arithmetic expressions (e.g. `bw_mod_5`)

        alpha : AlphaLevel, optional
            Transparency level of the entire text layer.

            Must be an integer from `1` (least opaque) to `9` (most opaque).

        typography : str, optional
            Text styling options.

            Supported values:
            - `"b"` (bold)
            - `"i"` (italic)
            - `"strikethrough"`
            - Any valid underscore-separated combination
            (e.g. `"b_i"`, `"b_i_strikethrough"`)

        background : str, optional
            background:
            - For Solid color, requires hex, RGBA hex or svg color name
            - For dominant color background, use "dominant"
            - For blurred background use
                background: {"blur_intensity": Union[int] = "auto", brightness: [-255 to 255]}
            - For Gradient background use
                background: {"mode": "dominant", "pallete_size": Literal[2,4]=2}

        corner_radius : NumberOrExpression, optional
            Corner radius for the text background box.

            Can be a positive number, arithmetic expression, or `"max"` to produce
            fully rounded corners (pill / oval shape).

        rotation : NumberOrExpression, optional
            Rotation angle of the text layer in degrees.

            Accepted forms:
            - Positive numbers (clockwise rotation)
            - Negative numbers or `N`-prefixed values (counter-clockwise)
            - Arithmetic expressions

        flip : FlipMode, optional
            Flips or mirrors the text layer.

            Supported values:
            - `"h"`   → horizontal flip
            - `"v"`   → vertical flip
            - `"h_v"` → both directions

        line_height : NumberOrExpression, optional
            Line height (spacing) between wrapped lines of text.

            Only takes effect when the text spans multiple lines.
            Accepts fixed numbers or arithmetic expressions.

        layer_mode : {"multiply", "cutout", "cutter"}, optional
            Blending mode for the text layer.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing a fully validated and normalized text overlay
            definition in the internal format expected by the ImageKit URL builder.

            Example structure:
            {
                "overlay": {
                    "type": "text",
                    "text": "...",
                    "position": {...},
                    "transformation": [{...}]
                }
            }
        """
        text_overlay = TextOverlay(
            text=text,
            layer_x=layer_x,
            layer_y=layer_y,
            width=width,
            font_size=font_size,
            font_family=font_family,
            color=color,
            inner_alignment=inner_alignment,
            padding=padding,
            alpha=alpha,
            typography=typography,
            background=background,
            corner_radius=corner_radius,
            rotation=rotation,
            flip=flip,
            line_height=line_height,
            layer_mode=layer_mode,
        )
        return await text_overlay.to_overlay_dict()
