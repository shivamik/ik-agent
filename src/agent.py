import os
import json
import argparse
from strands import Agent
from dotenv import load_dotenv
from strands.models.openai import OpenAIModel
import logging

from src.tools import tools  # Import the tools list from src.tools
from src.prompts import AGENT_SYSTEM_PROMPT

# Configure the root strands logger
logging.getLogger("strands").setLevel(logging.DEBUG)

# Add a handler to see the logs
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s", handlers=[logging.StreamHandler()]
)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
model = OpenAIModel(
    client_args={
        "api_key": OPENAI_API_KEY,
    },
    # **model_config
    model_id="gpt-5.1",
    params={
        "max_completion_tokens": 10000,
        "temperature": 0.7,
    },
)

agent = Agent(
    model=model,
    tools=tools,
    system_prompt=AGENT_SYSTEM_PROMPT,
)


def strands_agent_open_ai(payload):
    """
    Invoke the agent with a payload
    """
    user_input = payload.get("prompt")
    response = agent(user_input)
    return response.message["content"][0]["text"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", type=str)
    args = parser.parse_args()
    response = strands_agent_open_ai(json.loads(args.payload))
    print(response)
