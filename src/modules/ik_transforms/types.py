import re
from pydantic_core import core_schema
from typing import Any, Union, Literal, Optional
from pydantic import GetCoreSchemaHandler, BaseModel

_ALLOWED_VARS = "ih|iw|iar|idu|ch|cw|car|bh|bw|bar|bdu"
_OPS = "add|sub|mul|div|mod|pow"

_EXPR_REGEX = re.compile(
    rf"""
    ^
    (?:({_ALLOWED_VARS})|[0-9]+(?:\.[0-9]+)?)            # first value
    (?:
        _({_OPS})_
        (?:({_ALLOWED_VARS})|[0-9]+(?:\.[0-9]+)?)        # next value
    )*
    $
    """,
    re.VERBOSE,
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
                core_schema.float_schema(),
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
    def validate(value: Union[int, float, str]) -> Union[int, float, str]:
        if isinstance(value, (int, float)):
            return value

        if isinstance(value, str):
            if not _EXPR_REGEX.fullmatch(value):
                raise ValueError(f"Invalid ImageKit arithmetic expression: {value!r}")
            return value

        raise TypeError("Invalid type for NumberOrExpression")

    @staticmethod
    def serialize(value: Union[int, float, str]) -> str:
        if isinstance(value, (int, float)):
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
