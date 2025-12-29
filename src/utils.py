from glom import glom
from typing import Any, Optional


def maybe_filter(spec: Optional[Any], response: Any) -> Any:
    if spec:
        return glom(response, spec)
    return response
