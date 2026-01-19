import os
import logging
import typesense
import yaml
from typesense import Client
from openai import AsyncOpenAI
from pathlib import Path
from enum import Enum

# LOG_LEVEL = os.getenv("log_level", "INFO").upper()
LOG_LEVEL = "DEBUG"
if LOG_LEVEL == "INFO":
    LOG_LEVEL = logging.INFO
elif LOG_LEVEL == "DEBUG":
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO

logger = logging.getLogger("src.config")


TYPESENSE_CONVERSATION_BOT_PROMPT = """
You are a support assistant answering ImageKit-related queries.
You will always answer based only on the provided context.
Your job is not to recall prior knowledge, but to interpret and synthesize the relevant information already contained in the context.

When generating an answer:

Rely solely on the context. All explanations, examples, URLs, and parameters must come from it.

Prefer quoting or reusing phrasing from the context (e.g., transformation syntax, parameter names, or URL structures).

Use examples shown in the context to construct the most relevant solution for the user’s question.

If the context contains examples or parameter tables, apply those patterns directly to answer the query.

Do not add new parameters or syntax that do not appear anywhere in the context.

If some part of the answer is not clearly available in the context, explicitly say that it is not covered there.

Keep your answer factual, concise, and instructional. Avoid vague statements or advice to “refer to documentation.”

The final answer should look grounded — it should be obvious that it was built from the given text, not memory.
"""

TYPESENSE_MODEL_PAYLOAD = {
    "id": "imagekit_rag_chat_gpt-4.1",
    "model_name": "openai/gpt-4.1",
    "api_key": os.getenv("OPENAI_API_KEY"),
    "history_collection": "conversation_store",
    "system_prompt": TYPESENSE_CONVERSATION_BOT_PROMPT,
    "max_bytes": 40_000,
    "ttl": 86400,
}


def _get_typesense_client() -> Client:
    client = Client(
        {
            "api_key": os.getenv("TYPESENSE_API_KEY", ""),
            "nodes": [
                {
                    "host": os.getenv("TYPESENSE_HOST", ""),
                    "port": int(os.getenv("TYPESENSE_PORT", "443")),
                    "protocol": os.getenv("TYPESENSE_PROTOCOL", "https"),
                }
            ],
            "connection_timeout_seconds": 120,
        }
    )

    _ensure_conversation_store(client)
    _ensure_conversation_model(client)
    return client


def _ensure_conversation_store(client: Client) -> None:
    conversation_schema = {
        "name": "conversation_store",
        "fields": [
            {"name": "conversation_id", "type": "string"},
            {"name": "model_id", "type": "string"},
            {"name": "timestamp", "type": "int32"},
            {"name": "role", "type": "string", "index": False},
            {"name": "message", "type": "string", "index": False},
        ],
    }
    try:
        client.collections.create(conversation_schema)
        logger.info("Created Typesense conversation_store collection.")
    except typesense.exceptions.ObjectAlreadyExists:
        logger.debug("conversation_store collection already exists.")


def _ensure_conversation_model(client: Client) -> None:
    try:
        client.conversations_models.create(TYPESENSE_MODEL_PAYLOAD)
        logger.info("Created Typesense conversation model.")
    except typesense.exceptions.ObjectAlreadyExists:
        logger.debug("Conversation model already exists.")


OPENAI_CLIENT = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
TYPESENSE_CLIENT = _get_typesense_client()


TEMP_DIR = Path("temp")


IK_TRANSFORMS_CSV_PATH = Path("static/ik_transforms.csv")
IK_TRANSFORMS_METHOD_CAPABILITIES_PATH = Path(
    "static/transforms_method_capabilities.yaml"
)


class IK_Transforms(Enum):
    RESIZE_AND_CROP = "resize_and_crop"
    AI_TRANSFORM = "ai_transform"
    IMAGE_OVERLAY = "image_overlay"
    TEXT_OVERLAY = "text_overlay"


TIMEOUT_IMAGE_GENERATIO_SECONDS = 120
ARITHMETIC_EXPRESSION_FILE_PATH = "./static/arithmetic_expressions.yaml"

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
