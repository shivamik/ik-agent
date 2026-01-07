import os
import json
import re
import math
import logging
from enum import Enum
from glom import glom
from typing import Any, Optional, List


from src.config import OPENAI_CLIENT
from imagekitio.lib.helper import SUPPORTED_TRANSFORMS

logger = logging.getLogger()


def maybe_filter(spec: Optional[Any], response: Any) -> Any:
    if spec:
        return glom(response, spec)
    return response


class ImagekitInformationSource(Enum):
    ImagekitGuides = "imagekit_guides"
    ImagekitCommunity = "imagekit_community"
    ImagekitAPIReferences = "imagekit_api_references"
    ImagekitSDK = "imagekit_sdk"


DEFAULT_SOURCES = [
    ImagekitInformationSource.ImagekitGuides.value,
    ImagekitInformationSource.ImagekitCommunity.value,
]

DEV_SDK_KEYWORDS = [
    "python",
    "javascript",
    "java",
    "php",
    "ruby",
    "react-native",
    "react",
    "angular",
    "vue",
    "vuejs",
    "ios",
    "android",
    "nextjs",
    "sdk",
    "language",
]

API_REFERENCE_KEYWORDS = [
    r"\bapi\b",
    r"endpoint",
    r"rest",
    r"response",
    r"request",
    r"payload",
    r"parameter",
    r"query param",
    r"header",
    r"http",
    r"status code",
    r"authentication",
    r"public key",
    r"private key",
    r"signature",
    r"webhook",
    r"paginate",
    r"api key",
    r"upload api",
    r"media api",
    r"purge",
    r"list files",
    r"update details",
    r"rename file",
    r"delete file",
    r"purge cache",
    r"purge status",
    "upload file",
    "upload file v2",
    "create new field",
    "list all fields",
    "get file details",
    "update file details",
    "update existing field",
    "delete a field",
    "list and search assets",
    "delete file",
    "delete multiple files",
    "copy file",
    "move file",
    "rename file",
    "list file versions",
    "get file version details",
    "delete file version",
    "restore file version",
    "add tags bulk",
    "remove tags bulk",
    "remove ai tags bulk",
    "create folder",
    "delete folder",
    "copy folder",
    "move folder",
    "rename folder",
    "bulk job status",
    "purge cache",
    "purge status",
    "get uploaded file metadata",
    "get metadata from url",
    "get usage",
    "list origins",
    "create origin",
    "get origin",
    "update origin",
    "delete origin",
    "list url endpoints",
    "create url endpoint",
    "get url endpoint",
    "update url endpoint",
    "delete url endpoint",
]


def _l2_normalize(vec: List[float]) -> List[float]:
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0:
        return vec
    return [v / norm for v in vec]


def _round_floats(vec: List[float], digits: int) -> List[float]:
    return [round(v, digits) for v in vec]


async def embed_query(query: str) -> List[float]:
    client = OPENAI_CLIENT
    model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
    resp = await client.embeddings.create(model=model, input=query)
    vec = list(resp.data[0].embedding)
    vec = _l2_normalize(vec)
    return _round_floats(vec, 5)


async def get_query_keywords_using_model(query: str) -> list[str]:
    """Get query keywords via an LLM classifier."""
    client = OPENAI_CLIENT
    prompt = f"""
You are tasked to get all the keywords from the user query. You may refer to the following rules:

Rules:
- Get any api references, endpoints, parameters, authentication, error codes as keywords.
- If any language is present, include keyword as "language <language_name>".
- Get any transformation parameters as keywords.
- Get any technical terms as keywords.
- Ignore common words like "what", "is", "the", "a", "an", "how", "imagekit", "sdk"
- Get only specific keywords.
- Any numeric value along with parameter should be included as a single keyword. E.g. "resize 300x300"
- Any alphanumeric value along with parameter should be included as a single keyword. E.g. "text bold"

- Return JSON: {{"keywords": ["..."]}}

Query: "{query}"
"""
    output = []
    response = await client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    try:
        content = response.choices[0].message.content or "{}"
        keywords = json.loads(content).get("keywords")
        if keywords:
            output.extend(keywords)
            return list(set(output))
    except (json.JSONDecodeError, KeyError, IndexError):
        logger.warning("Failed to parse routing model response; using defaults.")
    return list(set(keywords))


def detect_sources(query: str) -> List[str]:
    sources = list(DEFAULT_SOURCES)
    query_lower = query.lower()

    if any(re.search(pattern, query_lower) for pattern in DEV_SDK_KEYWORDS):
        sources.append(ImagekitInformationSource.ImagekitSDK.value)

    if any(re.search(pattern, query_lower) for pattern in API_REFERENCE_KEYWORDS):
        sources.append(ImagekitInformationSource.ImagekitAPIReferences.value)
    return sources


SUPPORTED_TRANSFORMS_REV_MAP = {v: k for k, v in SUPPORTED_TRANSFORMS.items()}


def get_transform_key(transform_name: str) -> Optional[str]:
    if not transform_name:
        return transform_name
    return SUPPORTED_TRANSFORMS_REV_MAP.get(transform_name)
