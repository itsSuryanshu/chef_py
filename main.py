import base64
import io
import os
from datetime import datetime, timezone
from pathlib import Path
from pprint import pprint

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool
from langchain_tavily import TavilySearch
from PIL import Image

load_dotenv()
MODEL = os.getenv("OPENAI_MODEL_NAME", "gpt-5.4-mini")

search = TavilySearch(max_results=20, topic="general")

@tool
def extract_img(src: str) -> str:
    """Handles image path input and applies useful modifications to the image, then converts it to a base64 encoded string, then extracts the ingredients from the image."""
    imgSrc = Path(src).expanduser().resolve()
    img_str = None
    with Image.open(imgSrc) as img:
        img.thumbnail((1028, 1028))
        img = img.convert("RGB")
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    img_block = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}

    extract_prompt = """
    You are a helpful assistant that extracts ingredients from an image. You are given a base64 encoded string of an image. You need to extract the ingredients from the image.
    You have a keen eye for details and you are able to extract the ingredients from the image.
    
    CRITICAL BEHAVIORAL CONSTRAINTS:
    1. DO NOT invent or assume any ingredients. If you are unsure about an ingredient, you should not include them in the response.
    2. Do not include any other text in the response. Just return the ingredients.

    RESPONSE FORMAT:
    - Name out the ingredients in a single line, separated by commas. Do not include any other text in the response.
    """

    extractor = create_agent(
        model=MODEL,
        system_prompt=extract_prompt,
    )

    response = extractor.invoke(
        {"messages": [HumanMessage(content=[img_block])]}
    )
    return response["messages"][-1].content

@tool
def get_time_month() -> str:
    """Returns current time and month using date"""
    now = datetime.now(timezone.utc).astimezone()
    time_of_day = now.strftime("%I:%M%p %Z")
    month = now.strftime("%B")
    return f"{time_of_day} in {month}"

@tool
def search_recipes(ingredients: str) -> str:
    """Searches for recipes given a list of ingredients"""

    culinary_assistant_prompt = """
    You are a mindful culinary data assistant. You are given a list of raw ingredients and your absolute first goal is to gather context and external search data before proposing any recipes.

    CRITICAL BEHAVIORAL CONSTRAINTS:
    1. DO NOT invent, assume, or pre-determine any recipes or dish names before calling your tools. 
    2. You must execute your tool calls sequentially to build your knowledge base.

    EXECUTION STEPS:
    Step 1: Execute `get_time_month` to establish the exact baseline time context (season [winter, spring, summer, fall] and meal type [breakfast, lunch, dinner, or snacks]).
    Step 2: Formulate your `search_recipes` query. The search query parameter MUST ONLY contain the raw list of ingredients, the verified season, and the verified meal type. DO NOT inject specific recipe names (like "pumpkin soup" or "pancakes") into the search query text itself. Let the search engine discover what can be made.
    Step 3: Analyze the search results returned by the tool, and *only then* synthesize the final response into the two requested categories.

    FINAL RESPONSE CATEGORY GUIDELINES:
    1. Recipes that can be made with a set of given ingredients or all ingredients
    2. Recipes that are a good fit but not all ingredients are given, so suggest replacements for the missing ingredients

    CATEGORIES FOR FINAL RESPONSE:
    - Recipes that can be made with a set of given ingredients
    - Recipes that are a good fit with replacements for the missing ingredients
    """
    culinary_assistant = create_agent(
        model=MODEL,
        tools=[get_time_month, search],
        system_prompt=culinary_assistant_prompt
    )
    response = culinary_assistant.invoke(
        {"messages": [HumanMessage(content=ingredients)]}
    )
    return response["messages"][-1].content


def main() -> None:
    system_prompt = """
    You are a manager of this program. You are to orchestrate the execution of the program by calling the appropriate tools based on the input.

    CRITICAL BEHAVIORAL CONSTRAINTS:
    1. DO NOT assume or pre-determine the process of the program. You are to call the appropriate tools based on the input.
    2. DO NOT alter the input in any way. The image path or outputs from the tools must be used exactly as they are.
    2. You must not add any other text in the response. Just use your tools and their responses to synthesize the final response.

    EXECUTION STEPS:
    Step 1: Determine if the input is a list of raw ingredients or a path to an image of the ingredients.
    Step 2: If the input is a path to an image of the ingredients, execute `extract_img` with the exact path given to get the list of ingredients. Otherwise, skip execution of `extract_img` completely.
    Step 3: Call `search_recipes` with the list of ingredients to get the curated list of recipes.
    Step 4: Output the response from the `search_recipes` tool.
    """

    orchestrator = create_agent(
        model=MODEL,
        tools=[extract_img, search_recipes],
        system_prompt=system_prompt
    )

    response = orchestrator.invoke(
        {"messages": [HumanMessage(content="~/Downloads/ingredients1.jpg")]}
    )
    pprint(response)
    print(response["messages"][-1].content)

if __name__ == "__main__":
    main()
