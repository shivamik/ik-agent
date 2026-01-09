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
- x, y, x_center, y_center  [only for cm in {"extract","pad_extract"}; absolute vs relative ex_centerlusive]

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

from typing import Dict, Optional, Union, Literal, TypedDict
from src.utils.utils import get_transform_key, Any

logger = logging.getLogger("transforms.resize_and_crop")
logger.setLevel(logging.DEBUG)

NumberOrExpression = Union[int, float, str]


class ResizeAndCropParams(TypedDict, total=False):
    width: NumberOrExpression
    height: NumberOrExpression
    aspect_ratio: str
    crop: Literal["force", "at_max_enlarge", "at_least", "maintain_ratio"]
    crop_mode: Literal["pad_resize", "pad_extract", "extract"]
    focus: str
    zoom: NumberOrExpression
    x: NumberOrExpression
    y: NumberOrExpression
    x_center: NumberOrExpression
    y_center: NumberOrExpression
    dpr: NumberOrExpression
    background: str


class ResizeAndCropTransforms:
    """
    A validated transformation spec for ImageKit resize & crop parameters.

    Public API:
        resize_and_crop(...)-> Dict[str, str]

    The returned dict uses ImageKit's short keys:
        w, h, ar, c, cm, fo, z, x, y, x_center, y_center, dpr
    """

    # --- Enums from the resize/crop domain ---
    CROP_MODES = {"pad_resize", "pad_extract", "extract"}
    CROPS = {"force", "at_max_enlarge", "at_least", "maintain_ratio"}

    # --- COCO object classes (80) allowed for intelligent focus in `fo` ---
    COCO_CLASSES = {
        "person",
        "bicy_centerle",
        "car",
        "motorcy_centerle",
        "airplane",
        "bus",
        "train",
        "truck",
        "boat",
        "traffic_light",
        "fire_hydrant",
        "stop_sign",
        "parking_meter",
        "bench",
        "bird",
        "cat",
        "dog",
        "horse",
        "sheep",
        "cow",
        "elephant",
        "bear",
        "zebra",
        "giraffe",
        "backpack",
        "umbrella",
        "handbag",
        "tie",
        "suitcase",
        "frisbee",
        "skis",
        "snowboard",
        "sports_ball",
        "kite",
        "baseball_bat",
        "baseball_glove",
        "skateboard",
        "surfboard",
        "tennis_racket",
        "bottle",
        "wine_glass",
        "cup",
        "fork",
        "knife",
        "spoon",
        "bowl",
        "banana",
        "apple",
        "sandwich",
        "orange",
        "broccoli",
        "carrot",
        "hot_dog",
        "pizza",
        "donut",
        "cake",
        "chair",
        "couch",
        "potted_plant",
        "bed",
        "dining_table",
        "toilet",
        "tv",
        "laptop",
        "mouse",
        "remote",
        "keyboard",
        "cell_phone",
        "microwave",
        "oven",
        "toaster",
        "sink",
        "refrigerator",
        "book",
        "clock",
        "vase",
        "scissors",
        "teddy_bear",
        "hair_drier",
        "toothbrush",
    }

    # --- Focus buckets (context-dependent) ---
    _PAD_RESIZE_FO = {"left", "right", "top", "bottom"}  # padding position control
    _EXTRACT_RELATIVE_FO = {
        "center",
        "top",
        "bottom",
        "left",
        "right",
        "top_left",
        "top_right",
        "bottom_left",
        "bottom_right",
    }  # relative crop anchor
    _SPECIAL_FO = {"custom"}  # custom focus region
    _INTELLIGENT_FO = {"auto", "face"}  # plus COCO_CLASSES

    def resize_and_crop(
        self,
        **params: Any,
    ) -> Dict[str, str]:
        known: ResizeAndCropParams = {}
        extra: Dict[str, Any] = {}

        for k, v in params.items():
            if k in ResizeAndCropParams.__annotations__:
                known[k] = v
            else:
                extra[k] = v

        if extra:
            logger.debug("Ignoring unsupported params: %s", extra)

        return self._resize_and_crop_impl(**known)

    def _resize_and_crop_impl(
        self,
        *,
        width: Optional[NumberOrExpression] = None,
        height: Optional[NumberOrExpression] = None,
        aspect_ratio: Optional[str] = None,
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
        background: Optional[str] = None,
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
            Aspect ratio as "<w>-<h>" (e.g. "16-9") or an arithmetic expression string.

        crop : {"force","at_max_enlarge","at_least","maintain_ratio"}, optional
            Default: "maintain_ratio"
            Resize/crop strategy. Important:
            - When crop='force', focus and zoom are not allowed.

        crop_mode : {"pad_resize","pad_extract","extract"}, optional
            Crop mode controlling padding/extraction.
            - Coordinates (x,y,x_center,y_center) are ONLY allowed with crop_mode in {"extract","pad_extract"}.

        background: str, optional
            Background color for padding (hex without #, e.g. "FFFFFF" for white).

        focus : str, optional
            Focus parameter `fo` with context-sensitive values:

            Allowed depending on usage:
            - With crop_mode='pad_resize':
                left, right, top, bottom  (padding position control)
                auto, face, or any COCO class
            - With crop_mode in {'extract','pad_extract'}:
                center/top/left/bottom/right/top_left/top_right/bottom_left/bottom_right
                custom
                auto, face, or any COCO class
            - With crop='maintain_ratio':
                custom
                auto, face, or any COCO class

            Forbidden:
            - If crop='force', focus is not allowed.

        zoom : int | float | str, optional
            Zoom factor `z`. Must be > 0 when numeric.
            Forbidden when crop='force'.

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

        transforms: Dict[str, str] = {}

        # --- Basic sizing ---
        if width is not None:
            self._validate_dimension("width", width)
            transforms[get_transform_key("w")] = str(width)

        if height is not None:
            self._validate_dimension("height", height)
            transforms[get_transform_key("h")] = str(height)

        if aspect_ratio is not None:
            self._validate_non_empty_str("aspect_ratio", aspect_ratio)
            transforms[get_transform_key("ar")] = aspect_ratio

        # --- Crop & crop_mode enums ---
        if crop is not None:
            self._validate_enum("crop", crop, self.CROPS)
            transforms[get_transform_key("c")] = crop

        if crop_mode is not None:
            self._validate_enum("crop_mode", crop_mode, self.CROP_MODES)
            transforms[get_transform_key("cm")] = crop_mode

        # --- Focus & zoom restrictions with crop='force' ---
        if crop == "force":
            if focus is not None:
                raise ValueError("focus (fo) cannot be used when crop='force'")
            if zoom is not None:
                raise ValueError("zoom (z) cannot be used when crop='force'")

        # --- Focus validation (context-sensitive) ---
        if focus is not None:
            self._validate_focus(fo=focus, crop=crop, crop_mode=crop_mode)
            transforms[get_transform_key("fo")] = focus

        # --- Zoom validation ---
        if zoom is not None:
            self._validate_positive("zoom", zoom)
            transforms[get_transform_key("z")] = str(zoom)

        if background is not None:
            background = background.replace("#", "")
            transforms["background"] = str(background)

        # --- Positioning offsets (only for extract/pad_extract) ---
        if any(v is not None for v in (x, y, x_center, y_center)):
            if crop_mode not in {"extract", "pad_extract"}:
                raise ValueError(
                    "x, y, x_center, y_center are only allowed with crop_mode='extract' or 'pad_extract'"
                )

            # Prevent mixing absolute and center offsets
            if (x is not None or y is not None) and (
                x_center is not None or y_center is not None
            ):
                raise ValueError(
                    "Cannot mix absolute offsets (x,y) with center offsets (x_center,y_center)"
                )

            if x is not None:
                transforms[get_transform_key("x")] = str(x)
            if y is not None:
                transforms[get_transform_key("y")] = str(y)
            if x_center is not None:
                transforms[get_transform_key("x_center")] = str(x_center)
            if y_center is not None:
                transforms[get_transform_key("y_center")] = str(y_center)

        # --- DPR validation ---
        if dpr is not None:
            self._validate_positive("dpr", dpr)
            transforms[get_transform_key("dpr")] = str(dpr)

        return transforms

    # ------------------------------------------------------------------
    # Validators
    # ------------------------------------------------------------------

    def _validate_enum(self, name: str, value: str, allowed: set[str]) -> None:
        if value not in allowed:
            raise ValueError(
                f"{name} must be one of {sorted(allowed)} (got: {value!r})"
            )

    def _validate_non_empty_str(self, name: str, value: str) -> None:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty string")

    def _validate_dimension(self, name: str, value: NumberOrExpression) -> None:
        """
        Width/height accept:
        - numeric > 0
        - non-empty string (e.g., 'auto', arithmetic expressions)
        """
        if isinstance(value, (int, float)):
            if value <= 0:
                raise ValueError(f"{name} must be > 0 (got: {value})")
            return
        if isinstance(value, str) and value.strip():
            return
        raise ValueError(
            f"{name} must be a positive number or a non-empty string (got: {value!r})"
        )

    def _validate_positive(self, name: str, value: NumberOrExpression) -> None:
        """
        Accept:
        - numeric > 0
        - non-empty string (e.g., arithmetic expressions)
        """
        if isinstance(value, (int, float)):
            if value <= 0:
                raise ValueError(f"{name} must be > 0 (got: {value})")
            return
        if isinstance(value, str) and value.strip():
            return
        raise ValueError(
            f"{name} must be a positive number or a non-empty string (got: {value!r})"
        )

    def _validate_focus(
        self, *, fo: str, crop: Optional[str], crop_mode: Optional[str]
    ) -> None:
        """
        Validate `fo` (focus) with context-sensitive rules.

        Rules (as provided by user / ImageKit docs):

        - `fo` can be used along with:
            * pad_resize (crop_mode='pad_resize')
            * maintain_ratio (crop='maintain_ratio')
            * extract crop (crop_mode='extract' or 'pad_extract')

        - Allowed values depend on usage:
            * With pad_resize: left/right/top/bottom control padding position.
            * With maintain_ratio & extract: custom defines a specific focus area.
            * With extract: center/top/left/bottom/right/top_left/... define relative cropping anchor.
            * Additionally: intelligent focus values: auto, face, and COCO classes.
        """

        if not isinstance(fo, str) or not fo.strip():
            raise ValueError("focus (fo) must be a non-empty string")

        fo = fo.strip()

        # High-level compatibility: must belong to at least one supported context
        compatible = (
            (crop_mode == "pad_resize")
            or (crop == "maintain_ratio")
            or (crop_mode in {"extract", "pad_extract"})
        )
        if not compatible:
            raise ValueError(
                "focus (fo) is only valid with crop_mode='pad_resize', "
                "crop='maintain_ratio', or crop_mode in {'extract','pad_extract'}"
            )

        # Custom focus region (only for maintain_ratio or extract/pad_extract)
        if fo in self._SPECIAL_FO:
            if not (
                crop == "maintain_ratio" or crop_mode in {"extract", "pad_extract"}
            ):
                raise ValueError(
                    "custom is only valid with crop='maintain_ratio' or extract crop modes"
                )
            return

        # Intelligent focus: auto/face or COCO classes
        if (
            fo in self._INTELLIGENT_FO
            or fo in self.COCO_CLASSES
            or fo in self._EXTRACT_RELATIVE_FO
        ):
            return

        raise ValueError(f"Invalid focus (fo) value: {fo!r}")
