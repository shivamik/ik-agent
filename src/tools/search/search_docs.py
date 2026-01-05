import json
import os

from typing import Any, Dict, List, Optional
from strands import tool
from src.utils.utils import (
    embed_query,
    detect_sources,
    get_query_keywords_using_model,
    maybe_filter,
)
from src.config import TYPESENSE_CLIENT, TYPESENSE_MODEL_PAYLOAD

METADATA: Dict[str, Any] = {
    "resource": "search.docs",
    "operation": "read",
    "tags": [],
    "http_method": "post",
    "http_path": "/local/search/docs",
    "operation_id": "search-docs",
}


async def search_docs(
    *,
    query: str,
    sources: Optional[List[str]] = None,
    conversation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run a Typesense semantic chat query grounded in ImageKit docs.
    """
    resolved_sources = sources or detect_sources(query)
    keywords = await get_query_keywords_using_model(query)
    enriched_query = f"{query}, Keywords: {', '.join(keywords)}" if keywords else query

    vector = await embed_query(enriched_query)
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
        "filter_by": f"source:={resolved_sources}",
    }

    common_params: Dict[str, Any] = {
        "q": enriched_query,
        "conversation": True,
        "conversation_model_id": TYPESENSE_MODEL_PAYLOAD["id"],
    }
    if conversation_id:
        common_params["conversation_id"] = conversation_id

    payload = {"searches": [search_params]}
    return TYPESENSE_CLIENT.multi_search.perform(payload, common_params=common_params)


@tool(
    name="search_docs",
    description="""
            Search ImageKit docs/community/API references with RAG and return a grounded answer.
            This tool only search the imagekit docs and prepares answers for the user's queries.
            It can be used to answer questions about ImageKit features, API usage, transformation parameters, pricing, and other related topics.
            This tool does not perform any action relating to assets, accounts, or settings.
            This tool cannot create, modify, copy, move, save or delete any images or files.
            This is only a question answering tool.
            """,
)
async def search_docs_tool(
    query: str,
    sources: Optional[List[str]] = None,
    conversation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Search ImageKit documentation and return a grounded conversational answer.

    This Strands tool is a thin wrapper around `search_docs` that post-processes
    the Typesense response to return only the relevant conversational fields
    (answer and conversation ID).

    Args:
        query: The user's question about ImageKit features, APIs, pricing,
            transformations, or related topics.
        sources: Optional list of content sources to scope the search.
        conversation_id: Optional Typesense conversation ID to maintain
            conversational continuity across multiple queries.

    Returns:
        A dictionary containing:
            - answer: The grounded natural-language answer.
            - conversation_id: The Typesense conversation identifier, if present.
    """
    result = await search_docs(
        query=query,
        sources=sources,
        conversation_id=conversation_id,
    )

    return maybe_filter(
        {
            "answer": "conversation.answer",
            "conversation_id": "conversation.conversation_id",
        },
        result,
    )
