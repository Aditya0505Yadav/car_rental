import sys
import datetime
from crewai import Crew, Task, Agent
from browserbase import browserbase
from kayak import kayak_search
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os

# Load environment variables
load_dotenv()

# Get API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=GEMINI_API_KEY,
    temperature=0.7
)

# Create agents
cars_agent = Agent(
    role="Car Rentals Expert",
    goal="Search and analyze car rental options",
    backstory="I am an expert at finding the best car rental deals and analyzing options.",
    tools=[kayak_search, browserbase],
    llm=llm,
    verbose=True
)

summarize_agent = Agent(
    role="Summary Expert",
    goal="Provide clear and concise summaries of car rental options",
    backstory="I specialize in analyzing and summarizing complex information into clear recommendations.",
    llm=llm,
    verbose=True
)

# Create tasks
search_task = Task(
    description="""
    Search car rentals according to criteria {request}. Current year: {current_year}
    Provide a detailed analysis of the top 5 options.
    """,
    agent=cars_agent
)

summarize_task = Task(
    description="Create a clear summary of the rental options, highlighting the best deals",
    agent=summarize_agent
)

# Create crew
crew = Crew(
    agents=[cars_agent, summarize_agent],
    tasks=[search_task, summarize_task],
    verbose=True
)

if __name__ == "__main__":
    try:
        result = crew.kickoff(
            inputs={
                "request": "car rental in Miami from June 1st to June 5th",
                "current_year": datetime.date.today().year,
            }
        )
        print(result)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
