from dotenv import load_dotenv
load_dotenv()

# from langchain_ollama.llms import OllamaLLM
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from travel_plan_utils import weather_update_tool, wikidata_tool, overpass_poi_tool 
from travel_plan_utils import retrieve_relevant_docs, retrieve_relevant_docs_fn, web_search_tool
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader

# ----------------------------------------------------
# ✅ Set up OpenAI GPT-4 LLM
llm = ChatOpenAI(
    model="gpt-4o"
)

# llm = OllamaLLM(
#     model="gemma3:latest", 
#     base_url="http://localhost:11434"
# )

# ----------------------------------------------------
# ✅ Agents
guide_expert = Agent(
    role="City local guide Expert",
    goal="Provide interesting information about the city, things to do, places to eat.",
    backstory="A local expert who loves helping travelers discover hidden gems.",
    tools=[retrieve_relevant_docs, overpass_poi_tool, web_search_tool],
    verbose=True,
    max_iter=5,
    llm=llm
)

location_expert = Agent(
    role="Travel Logistics Expert",
    goal="Collect travel logistics like accommodations, costs, transportation, weather.",
    backstory="A seasoned travel expert who knows how to prepare for smooth trips.",
    tools=[retrieve_relevant_docs, weather_update_tool, web_search_tool],
    verbose=True,
    max_iter=5,
    llm=llm
)

planner_expert = Agent(
    role="Travel Planner",
    goal="Create a personalized travel plan based on gathered data.",
    backstory="An organizational wizard who turns data into practical itineraries.",
    tools=[retrieve_relevant_docs, overpass_poi_tool, weather_update_tool, wikidata_tool, web_search_tool],
    verbose=True,
    max_iter=5,
    llm=llm
)


# ----------------------------------------------------
# ✅ Functions to create tasks dynamically
def location_task(context, agent, from_city, destination_city, date_from, date_to, budget):
    return Task(
        description=f"""
In your response, use the retrieve_relevant_docs tool first to gather internal context, then use other appropriate tools.
Gather detailed travel logistics information, using internal database and web search, about {destination_city} for a traveler from {from_city}
planning to visit from {date_from} to {date_to}.
In a markdown report format include:
- Types of accommodations with examples.
- Estimated daily costs keeping in mind the {budget}.
- Transportation options. 
- For visa needs check visa pages for that {destination_city} country, and advisories.
- For weather check weather forcasts for {date_from} to {date_to} and major local events for the same time.
""",
        expected_output=f"""
After you finish your research, compile it into a markdown document only.
Use this format:

# Travel Information for {destination_city} 🏙️

## Accommodations 🏨
...

## Daily Costs 💰
...

## Transportation & Travel Tips 🚗✈️
...

## Weather & Events 🌦️🎉
...

Do NOT include thoughts, actions, or observations. Only the markdown document.
""",
        prompt_context=context,
        agent=agent,
        output_file=f'{destination_city}_report.md',
    )

def guide_task(context, agent, destination_city, interests, date_from, date_to, budget):
    return Task(
        description=f"""
In your response, use the retrieve_relevant_docs tool first to gather internal context, other appropriate tools.
Prepare a personalized city guide, using internal database and web search, for {destination_city} focused on interests: {interests}.
In a markdown report format include landmarks, dining options, outdoor activities, and any notable events or experiences.
""",
        expected_output=f"""
Once complete, produce a markdown document only, structured like:

# Personalized Itinerary for {destination_city} 🎯

- Each day activity suggestions.
- Find places to visit and recommend popular restaurants nearby, and also any prior reservations.
- Keep in mind the budget: {budget}.

No scratchpad, no chain-of-thought. Only markdown.
""",
        prompt_context=context,
        agent=agent,
        output_file=f'{destination_city}_guide_report.md',
    )

def planner_task(context, agent, destination_city, interests, date_from, date_to, budget):
    return Task(
        description=f"""
Use all gathered information about {destination_city} from location task and guide task.
Create a friendly introduction plus a day-by-day travel plan from {date_from} to {date_to} 
based on the traveler's interests: {interests} and budget: {budget}.
""",
        expected_output=f"""
Compile it all into a final markdown document using this format:

# Welcome to {destination_city} 🌆
- 1 to 2 paragraphs describing the city, its atmosphere, and why it's worth visiting.

# Here's Your Travel Plan 📅
- A markdown itinerary for each day with recommended times, places, meals, and short explanations with a cost estimate as well.
- For any recommendations add a link to an article that helps the person to decide on their best course.
- Give more personalized recommendations avoid general recommendations.

Add emojis to headings. Do NOT include thoughts, scratchpad, or tool calls — only produce the markdown.
""",
        context=context,
        agent=agent,
        output_file=f'{destination_city}_travel_plan.md',
    )

if __name__ == "__main__":

    # ✅ Input ------------------------

    from_city = "Boston"
    destination_city = "Rome"
    date_from = "3rd June 2026"
    date_to = "10th June 2026"
    interests = "sight seeing, good food and shopping"
    budget = "$5000"

    # Fetch internal context for RAG
    doc_context = retrieve_relevant_docs_fn(destination_city)
    if not doc_context:
        doc_context = "No internal documents were found for this topic."
    

    loc_task = location_task(doc_context, location_expert, from_city, destination_city, date_from, date_to, budget)
    guid_task = guide_task(doc_context, guide_expert, destination_city, interests, date_from, date_to, budget)
    plan_task = planner_task([loc_task, guid_task], planner_expert, destination_city, interests, date_from, date_to, budget)


    # ----------------------------------------------------
    # ✅ Build and run the crew
    crew = Crew(
        agents=[location_expert, guide_expert, planner_expert],
        tasks=[loc_task, guid_task, plan_task],
        process=Process.sequential,
        full_output=True,
        share_crew=False,
        verbose=True
    )

    result = crew.kickoff()

    print("\n✅ Travel planning workflow complete!")
    print(result)


    

