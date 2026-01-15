"""
Pydantic models for ImageKit **text layer** parameters (from the text overlay docs).

Covers:
- Text input: i / ie (with length limits)
- Positional params: lx / ly (numbers, N-prefixed negatives, arithmetic expressions)
- Text layer transformation params: w, fs, ff, co, ia, pa, al, tg, bg, r, rt, fl, lh

Assumes you already have NumberOrExpression + EXPR_REGEX as in your snippet.
"""

from __future__ import annotations

import re
from typing import Any, Optional, Union, Literal

from pydantic_core import core_schema
from pydantic import (
    GetCoreSchemaHandler,
    BaseModel,
)
# reuse your arithmetic expression regex
# EXPR_REGEX must already be defined

# padding shorthand: 1–4 positive integers separated by "_"
PADDING_SHORTHAND_REGEX = re.compile(r"^[1-9][0-9]*(?:_[1-9][0-9]*){0,3}$")

# Inner alignment
InnerAlignment = Literal["left", "center", "right"]

# Flip
FlipMode = Literal["h", "v", "h_v"]

# Radius
RadiusValue = Union[int, Literal["max"]]

ALLOWED_VARS = "ih|iw|iar|idu|ch|cw|car|bh|bw|bar|bdu"
OPS = "add|sub|mul|div|mod|pow"

EXPR_REGEX = re.compile(
    rf"""
    ^
    (?:({ALLOWED_VARS})|[0-9]+(?:\.[0-9]+)?)            # first value
    (?:
        _({OPS})_
        (?:({ALLOWED_VARS})|[0-9]+(?:\.[0-9]+)?)        # next value
    )*
    $
    """,
    re.VERBOSE,
)

FONT_FILE_REGEX = re.compile(
    r"""
    ^
    /?                                   # must start with /
    (?:[A-Za-z0-9._-]+/)*               # 0+ folders (no empty segments)
    [A-Za-z0-9._-]+                     # filename (no slashes)
    \.(?:ttf|otf|woff|woff2)            # allowed extensions
    $
    """,
    re.VERBOSE | re.IGNORECASE,
)

FONT_FAMILY = set(
    [
        "AbrilFatFace",
        "Amaranth",
        "Arvo",
        "Audiowide",
        "Chivo",
        "Crimson Text",
        "exo",
        "Fredoka One",
        "Gravitas One",
        "Kanit",
        "Lato",
        "Lobster",
        "Lora",
        "Monoton",
        "Montserrat",
        "PT Mono",
        "PT_Serif",
        "Open Sans",
        "Roboto",
        "Old Standard",
        "Ubuntu",
        "Vollkorn",
    ]
)


class NumberOrExpression:
    """
    ImageKit arithmetic scalar.

    - int / float:
        - negative → 'N{abs(value)}'
        - positive → str(value)
    - str:
        - must be a valid ImageKit arithmetic expression
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        # 1️⃣ base union
        union = core_schema.union_schema(
            [
                core_schema.int_schema(),
                core_schema.str_schema(),
            ]
        )

        # 2️⃣ validation wrapper
        validated = core_schema.no_info_plain_validator_function(cls.validate)

        # 3️⃣ serialization
        serializer = core_schema.plain_serializer_function_ser_schema(
            cls.serialize,
            return_schema=core_schema.str_schema(),
        )

        # 4️⃣ chain everything together
        return core_schema.chain_schema(
            [
                union,
                validated,
            ],
            serialization=serializer,
        )

    @staticmethod
    def validate(value: Union[int, str]) -> Union[int, str]:
        if isinstance(value, (int)):
            return value

        if isinstance(value, str):
            if not EXPR_REGEX.fullmatch(value):
                raise ValueError(f"Invalid ImageKit arithmetic expression: {value!r}")
            return value

        raise TypeError("Invalid type for NumberOrExpression")

    @staticmethod
    def serialize(value: Union[int, str]) -> str:
        if isinstance(value, (int)):
            if value < 0:
                return f"N{abs(value)}"
            return str(value)

        return value


class EUSM(BaseModel):
    radius: int
    sigma: int
    amount: float
    threshold: float


class EShadow(BaseModel):
    blur: int = 10
    saturation: int = 30
    x_offset: int = 2
    y_offset: int = 2


class EGradient(BaseModel):
    linear_direction: Union[int, str] = 180
    from_color: str = "FFFFFF"
    to_color: str = "000000"
    stop_point: Union[int, str] = 1


class EDistort(BaseModel):
    x1: NumberOrExpression
    y1: NumberOrExpression
    x2: NumberOrExpression
    y2: NumberOrExpression
    x3: NumberOrExpression
    y3: NumberOrExpression
    x4: NumberOrExpression
    y4: NumberOrExpression
    type: Literal["perspective", "arc"] = "perspective"
    arc_degree: Optional[int] = None


class PaddingValue:
    """
    ImageKit padding (pa).

    Accepts:
    - positive int (e.g. 10)
    - CSS-style shorthand strings: 10, 10_20, 10_20_30, 10_20_30_40
    - arithmetic expressions (e.g. bw_mod_5, bw_div_20)

    Rejects:
    - zero or negative values
    - mixed shorthand + expression
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        union = core_schema.union_schema(
            [
                core_schema.int_schema(),
                core_schema.str_schema(),
            ]
        )

        validator = core_schema.no_info_plain_validator_function(cls.validate)

        serializer = core_schema.plain_serializer_function_ser_schema(
            cls.serialize,
            return_schema=core_schema.str_schema(),
        )

        return core_schema.chain_schema(
            [union, validator],
            serialization=serializer,
        )

    @staticmethod
    def validate(value: Union[int, str]) -> Union[int, str]:
        # integer padding
        if isinstance(value, int):
            if value <= 0:
                raise ValueError("Padding must be a positive integer.")
            return value

        s = value.strip()

        # arithmetic expression
        if EXPR_REGEX.fullmatch(s):
            return s

        # shorthand form
        if PADDING_SHORTHAND_REGEX.fullmatch(s):
            return s

        raise ValueError(
            "Invalid padding value. Expected a positive integer, "
            "CSS shorthand (e.g. 10_20_30_40), or an arithmetic expression."
        )

    @staticmethod
    def serialize(value: Union[int, str]) -> str:
        return str(value)


class AlphaLevel:
    """
    ImageKit text/overlay transparency level (al).

    Supports:
    - integers from 1 to 9 (inclusive)
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        validator = core_schema.no_info_plain_validator_function(cls.validate)

        serializer = core_schema.plain_serializer_function_ser_schema(
            cls.serialize,
            return_schema=core_schema.str_schema(),
        )

        return core_schema.chain_schema(
            [core_schema.int_schema(), validator],
            serialization=serializer,
        )

    @staticmethod
    def validate(value: int) -> int:
        if not (1 <= value <= 9):
            raise ValueError("Alpha level (al) must be an integer between 1 and 9.")
        return value

    @staticmethod
    def serialize(value: int) -> str:
        return str(value)
