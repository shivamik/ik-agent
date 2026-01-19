"""
imagekit_transform_router.py

Unified ImageKit transformation router.

Flow:
1. Classify user intent using a small LLM (methods + tags)
2. Attempt structured transformation planning using CSV metadata
3. If structured planning fails or is incomplete:
   - Search ImageKit docs
   - Extract doc-supported parameters conservatively
4. Return BOTH:
   - structured_plan (authoritative)
   - doc_params (advisory fallback)

This module NEVER:
- Builds URLs
- Uses ImageKit short keys
- Hallucinates parameters
"""

import os
import yaml
import json
import logging
from typing import Any, Dict, List, Optional

import pandas as pd

from toon_format import encode

from src.config import (
    TYPESENSE_CLIENT,
    TYPESENSE_MODEL_PAYLOAD,
    OPENAI_CLIENT,
    IK_TRANSFORMS_METHOD_CAPABILITIES_PATH,
    IK_TRANSFORMS_CSV_PATH,
    IK_Transforms,
)
from src.utils.utils import ImagekitInformationSource, embed_query, get_transform_key
from src.prompts import (
    TRANSFORMATION_BUILDER_METHOD_CLASSIFIER_PROMPT_TEMPLATE,
    TRANSFORMATION_BUILDER_PARAMS_BUILDER_PROMPT_TEMPLATE,
    TRANSFORMATION_BUILDER_IK_DOC_PARAM_EXTRACTION_PROMPT,
)
from .transforms.resize_n_crop import ResizeAndCropTransforms
from .transforms.ai_transforms import AITransforms
from .transforms.image_overlay import ImageOverlayTransforms
from .transforms.text_overlay import TextOverlayTransforms
from .transforms.effects_and_enhancement import EffectsAndEnhancementTransforms

with open(IK_TRANSFORMS_METHOD_CAPABILITIES_PATH, "r") as f:
    method_n_capabilities = yaml.safe_load(f)

# Shared aliases to improve readability
TransformPlan = List[Dict[str, Any]]
# Logger
logger = logging.getLogger("transform_builder")
# ---------------------------------------------------------------------
# Environment & client
# ---------------------------------------------------------------------

VALID_METHODS: List[str] = list(method_n_capabilities.keys())

VALID_METHODS_DOCS_STRINGS = {
    "resize_n_crop": ResizeAndCropTransforms._resize_and_crop_impl.__doc__,
    "ai_transforms": AITransforms._ai_transform_impl.__doc__,
    "image_overlay": ImageOverlayTransforms._image_overlay_impl.__doc__,
    "text_overlay": TextOverlayTransforms._text_overlay_impl.__doc__,
    "effects_and_enhancement": EffectsAndEnhancementTransforms._effects_and_enhancement_impl.__doc__,
}

# ---------------------------------------------------------------------
# CSV metadata loading
# ---------------------------------------------------------------------


def load_transform_metadata(csv_path: str) -> pd.DataFrame:
    """Load and normalize ImageKit transformation metadata."""
    df = pd.read_csv(csv_path)
    return df


# ---------------------------------------------------------------------
# Small LLM – intent classifier
# ---------------------------------------------------------------------


def build_small_llm_prompt(
    user_query: str,
    valid_methods: List[str],
) -> str:
    """Render the strict classification prompt for the small LLM."""
    return TRANSFORMATION_BUILDER_METHOD_CLASSIFIER_PROMPT_TEMPLATE.format(
        user_query=user_query,
        methods_json=encode(valid_methods),
    )


async def small_llm_filter(
    user_query: str,
    valid_methods: Dict[str, Any],
) -> Dict[str, List[str]]:
    """Classify user intent into methods."""
    prompt = build_small_llm_prompt(
        user_query=user_query,
        valid_methods=valid_methods,
    )

    response = await OPENAI_CLIENT.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You output JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    return json.loads(response.choices[0].message.content)


# ---------------------------------------------------------------------
# Deterministic CSV filtering
# ---------------------------------------------------------------------


def filter_metadata(
    df: pd.DataFrame,
    methods: List[str],
) -> TransformPlan:
    """Filter CSV rows using method match and tag intersection."""
    method_set = set(methods)

    def _row_matches(row: pd.Series) -> bool:
        method_matches = not method_set or row.get("method_name") in method_set
        return method_matches

    mask = df.apply(_row_matches, axis=1)
    return df[mask].to_dict(orient="records")


# ---------------------------------------------------------------------
# Big LLM – structured generator
# ---------------------------------------------------------------------


async def big_llm_generate(
    user_query: str,
    filtered_metadata: List[Dict[str, str]],
) -> List[Dict[str, Any]]:
    """Generate structured transform plan."""
    prompt = TRANSFORMATION_BUILDER_PARAMS_BUILDER_PROMPT_TEMPLATE.format(
        user_query=user_query,
        metadata=encode(filtered_metadata),
    )

    response = await OPENAI_CLIENT.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You output JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    return json.loads(response.choices[0].message.content)


# ---------------------------------------------------------------------
# Docs-based fallback (search_docs + extractor)
# ---------------------------------------------------------------------


def flatten_search_docs(search_docs_result: Dict[str, Any]) -> str:
    """Flatten grouped search_docs output for LLM consumption."""
    blocks = []
    for url, data in search_docs_result.items():
        blocks.append(
            f"""
SOURCE: {url}
TITLE: {data.get("page_title")}
DESCRIPTION: {data.get("page_description")}

CONTENT:
{data.get("content")}
""".strip()
        )
    return "\n\n---\n\n".join(blocks)


async def extract_params_from_docs(
    user_query: str,
    search_docs_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Extract advisory parameters from docs."""
    prompt = TRANSFORMATION_BUILDER_IK_DOC_PARAM_EXTRACTION_PROMPT.format(
        user_query=user_query,
        doc_context=flatten_search_docs(search_docs_result),
    )

    response = await OPENAI_CLIENT.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You output JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {}


async def search_docs(
    query: str,
    sources: Optional[List[str]] = None,
    conversation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run a Typesense semantic chat query grounded in ImageKit docs.
    """
    sources = sources or [
        ImagekitInformationSource.ImagekitGuides.value,
        ImagekitInformationSource.ImagekitCommunity.value,
    ]

    vector = await embed_query(query)
    embed_str = json.dumps(vector, separators=(",", ":"))

    search_params = {
        "collection": os.getenv("TYPESENSE_COLLECTION", ""),
        "query_by": (
            "section_content,summary,page_description,keywords,"
            "lvl0,lvl1,lvl2,lvl3,lvl4,lvl5,lvl6"
        ),
        "query_by_weights": "3,2,2,1,1,1,1,1,1,1,1",
        "vector_query": f"content_embedding:({embed_str},k:60)",
        "limit": 10,
        "rerank_hybrid_matches": True,
        "exclude_fields": "content_embedding",
        "filter_by": f"source:={sources}",
    }

    common_params: Dict[str, Any] = {
        "q": query,
        "conversation": False,
        "conversation_model_id": TYPESENSE_MODEL_PAYLOAD["id"],
    }
    if conversation_id:
        common_params["conversation_id"] = conversation_id

    payload = {"searches": [search_params]}
    logger.debug("typesense.search_docs query=%s sources=%s", query, sources)
    return TYPESENSE_CLIENT.multi_search.perform(payload, common_params=common_params)


def group_search_results(search_results: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """Group Typesense multi-search hits by `source_url` for downstream LLM use."""

    # Sort by rank (desc) then line order (asc) to retain doc flow
    fused_sorted = sorted(
        search_results["results"][0]["hits"],
        key=lambda x: (x.get("hybrid_search_info").get("rank_fusion_score")),
        reverse=True,
    )
    fused_sorted = sorted(
        fused_sorted,
        key=lambda x: (
            x.get("source_url", ""),
            x.get("line_start", float("inf")),
        ),
    )

    final_docs: dict[str, dict] = {}

    for doc in fused_sorted:
        doc = doc["document"]
        source_url = doc.get("source_url")
        if not source_url:
            # Skip if no source_url (invalid record)
            continue

        # Initialize file-level structure if not already present
        file_entry = final_docs.setdefault(
            source_url,
            {
                "page_title": doc.get("lvl0", ""),
                "page_description": doc.get("page_description", ""),
                "content": "",
            },
        )

        # Build breadcrumb from lvl1–lvl6 hierarchy
        breadcrumb = " > ".join(
            doc.get(f"lvl{x}") for x in range(1, 7) if doc.get(f"lvl{x}")
        )

        # Compose formatted section block
        section_content = doc.get("section_content", "").strip()
        summary = doc.get("summary", "").strip()

        section_block = (
            f"\n"
            f"## {breadcrumb or '(No Section Title)'}\n"
            f"**Summary:** {summary or '(No summary)'}\n\n"
            f"{section_content}\n"
            f"---\n"
        )

        # Append section block to this page’s content
        file_entry["content"] += section_block

    return final_docs


def parse_params(
    method: str,
    params: Dict[str, Any],
):
    """Parse and normalize parameters based on method capabilities."""
    if method == IK_Transforms.RESIZE_AND_CROP.value:
        return ResizeAndCropTransforms().resize_and_crop(**params)
    elif method == IK_Transforms.AI_TRANSFORM.value:
        return AITransforms().ai_transform(**params)
    elif method == IK_Transforms.IMAGE_OVERLAY.value:
        return ImageOverlayTransforms().image_overlay(**params)
    elif method == IK_Transforms.TEXT_OVERLAY.value:
        return TextOverlayTransforms().text_overlay(**params)
    elif method == IK_Transforms.EFFECTS_AND_ENHANCEMENT.value:
        return EffectsAndEnhancementTransforms().effects_and_enhancement(**params)
    return params


def build_final_transformations(
    structured_plan: TransformPlan,
    doc_params: Optional[Dict[str, Any]] = None,
) -> TransformPlan:
    """
    Build the final ImageKit transformation list from structured (CSV-based)
    and doc-extracted (fallback) parameters.

    Precedence rules
    ----------------
    1. Structured plan (CSV + big LLM) is authoritative.
    2. Doc params are advisory and ONLY:
       - augment the base transformation
       - never override existing structured parameters
    3. Overlay transformations are preserved as separate steps.
    4. All parameter names are converted to ImageKit short keys.

    Parameters
    ----------
    structured_plan : list of dict
        Output from big LLM:
        [
          { "method": "...", "params": {...} },
          ...
        ]

    doc_params : dict, optional
        Output from docs extractor:
        {
          "params": { "<long_param>": <value> }
        }

    Returns
    -------
    list of dict
        Final ImageKit-ready transformations, e.g.
        [
          { "w": 300, "h": 300, "fo": "face" },
          { "l-text": "...", ... }
        ]
    """

    final_transforms: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # CASE 1: Structured plan exists (primary path)
    # ------------------------------------------------------------------
    if structured_plan:
        logger.info(
            "Applying structured plan with %d step(s) and doc_params=%s",
            len(structured_plan),
            bool(doc_params),
        )

        for step in structured_plan:
            method = step.get("method", "")
            params = parse_params(method, step.get("params", {}))
            # params = step.get("params", {})

            if not params:
                logger.debug("Skipping step with no params for method=%s", method)
                continue

            if isinstance(params, list):
                for p in params:
                    final_transforms.append(p)
            else:
                final_transforms.append(params)
        # Apply doc params ONLY if not already set
        if doc_params and doc_params.get("params"):
            logger.debug("There are doc params of len: ", len(doc_params["params"]))
            fallback_transform: Dict[str, Any] = {}
            for long_key, value in doc_params["params"].items():
                if value:
                    fallback_transform[get_transform_key(long_key)] = value
            if fallback_transform:
                # Overlay doc params as a new step
                final_transforms.append(fallback_transform)

    # ------------------------------------------------------------------
    # CASE 2: No structured plan → docs-only fallback
    # ------------------------------------------------------------------
    if doc_params and doc_params.get("params"):
        fallback_transform: Dict[str, Any] = {}

        for long_key, value in doc_params["params"].items():
            if value:
                fallback_transform[get_transform_key(long_key)] = value

        if fallback_transform:
            final_transforms.append(fallback_transform)

    logger.info("Built %d transformation(s)", len(final_transforms))
    return final_transforms


# ---------------------------------------------------------------------
# PUBLIC ROUTER FUNCTION
# ---------------------------------------------------------------------


async def resolve_imagekit_transform(
    user_query: str,
) -> List[Dict[str, Any]]:
    """
    Resolve ImageKit transformation intent into ImageKit-ready transformations.

    Workflow:
    1) Load CSV-backed metadata to anchor the structured plan.
    2) Classify the user request into valid methods/tags via a small LLM.
    3) Generate a structured plan with a larger model, constrained to metadata.
    4) If missing/uncertain, search docs and extract advisory params.
    5) Merge structured and advisory params, preferring structured values.
    """
    logger.info("Resolving transform for query: %s", user_query)
    df = load_transform_metadata(IK_TRANSFORMS_CSV_PATH)

    classification = await small_llm_filter(
        user_query=user_query,
        valid_methods=method_n_capabilities,
    )
    logger.info("Classification result: %s", classification)

    classified_methods = classification.get("methods", [])
    # unresolved_intent = classification.get("unresolved_intent")
    unresolved_intent = None

    filtered_metadata = filter_metadata(
        df=df,
        methods=classified_methods,
    )
    logger.info(
        "Filtered %d metadata entries using methods=%s",
        len(filtered_metadata),
        classified_methods,
    )

    output_metadata = []
    for method_meta_data in filtered_metadata:
        method_name = method_meta_data.get("method_name")
        output_metadata.append(
            {
                "method": method_name,
                "method_description": VALID_METHODS_DOCS_STRINGS.get(method_name, ""),
                "method_metadata": method_meta_data,
            }
        )

    structured_plan: TransformPlan = []

    if output_metadata:
        structured_plan = await big_llm_generate(
            user_query=user_query,
            filtered_metadata=output_metadata,
        )
        logger.info("Structured plan steps: %d", len(structured_plan))
        logger.info(
            f"Structured plan steps: {structured_plan}",
        )
    doc_params: Dict[str, Any] = {}
    should_query_docs = not structured_plan or bool(unresolved_intent)

    if should_query_docs:
        logger.info(
            "Falling back to docs search (unresolved=%s, structured=%s)",
            bool(unresolved_intent),
            bool(structured_plan),
        )
        search_query = unresolved_intent or user_query
        raw_results = await search_docs(query=search_query)
        grouped = group_search_results(raw_results)
        doc_params = await extract_params_from_docs(
            user_query=search_query,
            search_docs_result=grouped,
        )
        logger.info("Extracted %d doc param(s)", len(doc_params.get("params", {})))

    logger.info(f"{structured_plan}, {doc_params}")

    transformations = build_final_transformations(
        structured_plan=structured_plan,
        doc_params=doc_params,
    )
    return transformations
