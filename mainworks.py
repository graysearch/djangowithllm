import os
import datetime
import openai
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

# Add this right after creating your FastAPI app instance

# Set your OpenAI API key (ensure that the environment variable is set)
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],  # Your Django URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- Function to Generate a Response from OpenAI ---
def get_openai_response(messages):
    """
    Sends conversation messages to OpenAI and gets a response.
    Uses temperature=0 as specified.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Replace with your desired model if needed
        messages=messages,
        temperature=0  # Temperature is always 0
    )
    return response.choices[0].message.content

# --- Function to Generate a Sport Description using the LLM ---
def generate_sport_description(sport: str) -> str:
    """
    Builds a conversation with the LLM to generate a description of how the sport is played.
    """
    system_prompt = (
        """ You are a knowledgeable sports analyst. 
        Provide a detailed and clear description of how the sport is played.
         Always include the following CSS at the beginning of your responses:
        
       <style>
        h1 {color: #004e64; font-size: 28px; border-bottom: 2px solid #e63946; padding-bottom: 5px;}
        h2 {color: #00a5cf; font-size: 24px; border-bottom: 1px solid #457b9d; padding-bottom: 3px;}
        h3 {color: #25a18e; font-size: 20px;}
        .bullet-heading {font-weight: bold; text-decoration: underline;}
        </style>
        
        After adding the style, format your content with:
        - # for main sections (deep navy bule)
        - ## for subsections (blue)
        - ### for sub-subsections (lighter blue)
        
        For bullet points, use this format:
        - <span class="bullet-heading">Heading:</span> Rest of the bullet point text
        



        """        
    )
    # Build the conversation history with system and user messages.
    conversation_history = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Describe how {sport} is played."}
    ]
    # Call the LLM and return its response.
    description = get_openai_response(conversation_history)
    return description

@app.get("/sport-info")
def get_sport_info(sport: str):
    """
    Endpoint to get a description of how a sport is played.
    It calls the LLM to generate the description.
    Acceptable sports: soccer, cricket, basketball.
    """
    sport_lower = sport.lower()
    if sport_lower not in ["soccer", "cricket", "basketball"]:
        raise HTTPException(
            status_code=404,
            detail="Sport not found. Please choose from soccer, cricket, or basketball."
        )
    # Generate sport description via LLM
    description = generate_sport_description(sport_lower)
    return {"sport": sport_lower, "description": description}

# --- Data Model for GPT Query Request ---
class GPTQuery(BaseModel):
    query: str
    sport: str = None
    sport_info: str = None

@app.post("/gpt")
def process_query(query_request: GPTQuery):
    """
    Process the user's query with context by constructing a prompt and calling the OpenAI API.
    """
    if query_request.sport and query_request.sport_info:
        context = (
            f"Sport: {query_request.sport}. "
            f"Description: {query_request.sport_info}. "
            f"Question: {query_request.query}"
        )
    else:
        context = query_request.query

    # Build the conversation history for OpenAI
    conversation_history = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": context}
    ]

    # Call the OpenAI API using our helper function
    response_text = get_openai_response(conversation_history)
    return {"response": response_text}

@app.get("/logfile.log", response_class=PlainTextResponse)
async def get_logfile():
    """
    Endpoint to serve the log file content from a specific location
    """
    # Define specific log file path - change this to your actual log file location
    LOG_FILE_PATH = "/Users/amol/Documents/LLM/sportsproject/logfile.log"  # Update this path
    
    try:
        # Check if file exists
        if not os.path.exists(LOG_FILE_PATH):
            return "Log file not found"
        
        # Read the log file
        with open(LOG_FILE_PATH, "r") as f:
            content = f.read()
        
        return content
    except Exception as e:
        return f"Error reading log file: {str(e)}"