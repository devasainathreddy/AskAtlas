"""Weather agent node."""

import asyncio
from langchain_core.messages import HumanMessage

from src.config import get_settings, get_llm
from src.graph.state import AgentState
from src.tools.weather_tool import get_weather


def weather_agent_node(state: AgentState) -> dict:
    """Execute weather agent to fetch weather data.
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with weather result
    """
    settings = get_settings()
    
    # Get the weather query (either extracted or full query)
    query = state.get("weather_query") or state["query"]
    
    # Extract cities from query using LLM
    llm = get_llm(temperature=0)
    
    city_prompt = f"""Extract all city names from this query. Return ONLY the city names separated by commas, nothing else.
For abbreviations: BLR=Bangalore, HYD=Hyderabad, DEL=Delhi, MUM=Mumbai, CHE=Chennai, KOL=Kolkata
Query: {query}
Cities:"""
    
    city_response = llm.invoke([HumanMessage(content=city_prompt)])
    
    # Safely extract content
    content = city_response.content
    if isinstance(content, list):
        content = " ".join(str(c) for c in content)
    cities_text = str(content).strip()
    
    # Parse multiple cities
    cities = [c.strip() for c in cities_text.split(",") if c.strip()]

    if not cities:
        return {
            "weather_result": "I couldn't identify a city in your weather query.",
            "messages": [{"role": "assistant", "content": "No city could be extracted from the query"}],
        }

    # Fetch weather for all cities
    weather_results = []
    for city in cities:
        try:
            result = asyncio.run(get_weather.ainvoke({"city": city}))
            weather_results.append(result)
        except Exception as e:
            weather_results.append(f"Error fetching weather for {city}: {str(e)}")

    combined_result = "\n\n".join(weather_results)

    return {
        "weather_result": combined_result,
        "messages": [{"role": "assistant", "content": f"Weather data fetched for {', '.join(cities)}"}],
    }

