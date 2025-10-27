from crewai.tools import tool
import requests
import urllib.parse
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from dotenv import load_dotenv
import os

load_dotenv()  # loads variables from .env

# Load FAISS index from local folder
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local("data/faiss_index", embedding_model, allow_dangerous_deserialization=True)



# ----------------------------------------------------
# ✅ Web search and RAG Tool
@tool
def web_search_tool(query: str):
    """
    Perform a DuckDuckGo web search for the given query and return results.
    """
    search_tool = DuckDuckGoSearchResults(num_results=10, verbose=True)
    return search_tool.run(query)

def retrieve_relevant_docs_fn(query: str):
    """
    Searches the FAISS vector database for relevant travel information based on the query.
    """
    docs = vectorstore.similarity_search(query, k=5)
    if not docs:
        return "No relevant documents were found in the internal database."
    internal_context = "\n\n".join([doc.page_content for doc in docs])
    return internal_context

@tool
def retrieve_relevant_docs(query: str):
    """Tool version for CrewAI agents."""
    return retrieve_relevant_docs_fn(query)

# ----------------------------------------------------
# ✅ Weather, Wikidata & POI tool

@tool
def weather_update_tool(city: str):
    """
    Returns real-time weather info for a city using OpenWeatherMap API.
    """
    api_key = os.getenv("OPENWEATHERMAP_API_KEY")  # Replace with your OpenWeatherMap API key
    encoded_city = urllib.parse.quote(city)
    endpoint = f"http://api.openweathermap.org/data/2.5/weather?q={encoded_city}&appid={api_key}&units=metric"

    try:
        response = requests.get(endpoint)
        data = response.json()
        description = data['weather'][0]['description']
        temp_c = data['main']['temp']
        temp_f = (temp_c * 9/5) + 32

        return (
            f"Current weather in {city}:\n"
            f"- Description: {description}\n"
            f"- Temperature: {temp_c:.1f}°C / {temp_f:.1f}°F"
        )
    except Exception as e:
        return f"Weather info unavailable for {city}. Error: {str(e)}"
    
@tool
def wikidata_tool(city: str) -> str:
    """
    Returns top 5 tourist attractions in a city using Wikidata SPARQL.
    """
    query = f"""
    SELECT ?placeLabel WHERE {{
      ?place wdt:P31/wdt:P279* wd:Q570116;  # Instance of tourist attraction
             wdt:P131* ?location.
      ?location rdfs:label "{city}"@en.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }} LIMIT 5
    """
    url = "https://query.wikidata.org/sparql"
    headers = {"Accept": "application/sparql-results+json"}
    try:
        r = requests.get(url, params={'query': query}, headers=headers)
        results = r.json()["results"]["bindings"]
        places = [res["placeLabel"]["value"] for res in results]
        return f"Top tourist attractions in {city}:\n" + "\n".join(places) if places else "No tourist attractions found."
    except Exception as e:
        return f"Failed to retrieve Wikidata attractions. Error: {str(e)}"
    
@tool
def overpass_poi_tool(city: str, poi_types: str = "attraction") -> str:
    """
    Returns a list of points of interest (POIs) in the given city for the given types using Overpass API.
    Multiple POI types can be passed as a comma-separated string (e.g., "museum,cafe").
    """

    try:
        # Get bounding box of the city using Nominatim
        encoded_city = urllib.parse.quote(city)
        nominatim_url = f"https://nominatim.openstreetmap.org/search?q={encoded_city}&format=json"
        response = requests.get(nominatim_url, headers={"User-Agent": "rag-agent"})
        city_data = response.json()

        if not city_data:
            return f"Could not find location for '{city}'."

        south, north, west, east = city_data[0]["boundingbox"]

        # Create Overpass query for each POI type
        types = [t.strip() for t in poi_types.split(",")]
        filters = "\n".join(
            f'node["tourism"="{t}"]({south},{west},{north},{east});\n'
            f'node["amenity"="{t}"]({south},{west},{north},{east});'
            for t in types
        )

        overpass_query = f"""
        [out:json][timeout:25];
        (
            {filters}
        );
        out body;
        """

        # Request POIs from Overpass API
        overpass_response = requests.post("https://overpass-api.de/api/interpreter", data=overpass_query)
        elements = overpass_response.json().get("elements", [])

        # Format and return POI names
        pois = []
        for el in elements:
            name = el.get("tags", {}).get("name")
            category = el.get("tags", {}).get("amenity") or el.get("tags", {}).get("tourism")
            if name:
                pois.append(f"- {name} ({category})")

        if not pois:
            return f"No POIs found for {poi_types} in {city}."

        return f"Top POIs in {city}:\n" + "\n".join(pois[:15])

    except Exception as e:
        return f"Error retrieving POIs for {city}. {str(e)}"




