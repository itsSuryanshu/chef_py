from dotenv import load_dotenv
import os
from datetime import datetime, timezone
from pprint import pprint

from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_tavily import TavilySearch
from langchain.tools import tool

@tool
def get_time_month() -> str:
    """Returns current time and month using date"""
    now = datetime.now(timezone.utc).astimezone()
    time_of_day = now.strftime("%I:%M%p %Z")
    month = now.strftime("%B")
    return f"{time_of_day} in {month}"

def main() -> None:
    load_dotenv()
    MODEL = os.getenv("OPENAI_MODEL_NAME", "gpt-5.4-mini")
    search_recipes = TavilySearch(max_results=10, topic="general")

    system_prompt = """
    You are a mindful culinary data assistant. You are given a list of raw ingredients, and your absolute first goal is to gather context and external search data before proposing any recipes.

    CRITICAL BEHAVIORAL CONSTRAINTS:
    1. DO NOT invent, assume, or pre-determine any recipes or dish names before calling your tools. 
    2. You must execute your tool calls sequentially to build your knowledge base.

    EXECUTION STEPS:
    Step 1: Execute `get_time_month` to establish the exact baseline time context (season and meal type).
    Step 2: Formulate your `search_recipes` query. The search query parameter MUST ONLY contain the raw list of ingredients, the verified season, and the verified meal type. DO NOT inject specific recipe names (like "pumpkin soup" or "pancakes") into the search query text itself. Let the search engine discover what can be made.
    Step 3: Analyze the search results returned by the tool, and *only then* synthesize the final response into the two requested categories.

    CATEGORIES FOR FINAL RESPONSE:
    - Recipes that can be made with a set of given ingredients or all ingredients
    - Recipes that are a good fit but not all ingredients are given, so suggest replacements for the missing ingredients
    """

    agent = create_agent(
        model=MODEL,
        tools=[search_recipes, get_time_month],
        system_prompt=system_prompt
    )

    response = agent.invoke(
        {"messages": [HumanMessage(content="I have these ingredients: eggs, stale bread, milk, cheese, and onions. What recipes can I make?")]}
    )
    pprint(response)
    print(response["messages"][-1].content)

if __name__ == "__main__":
    main()
