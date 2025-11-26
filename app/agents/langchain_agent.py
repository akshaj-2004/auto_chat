
"""
This file defines:
- The LLM (Ollama - local LLM with native tool calling)
- Descriptions of tools (used by the agent)
- A helper to create an agent with tools
"""

from dotenv import load_dotenv
import os
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

llm = ChatOllama(
    model="llama3.1",
    temperature=0
)

TOOL_DESCRIPTIONS = {
    "create_registration":
        "Creates a new user registration. "
        "⚠️ WARNING: Do NOT call this tool unless the user has explicitly provided ALL real data. "
        "Do NOT use example values like 'John Doe', 'john.doe@example.com', or '1234567890'. "
        "If the user hasn't provided real data, ASK them for it instead of calling this tool. "
        "ALL fields are REQUIRED and must be provided. "
        "Parameters: "
        "- full_name (string): User's REAL full name, e.g. 'Alice Smith' "
        "- email (string): User's REAL email address, e.g. 'alice@example.com' "
        "- phone (string): User's REAL phone number, e.g. '5551234567' "
        "- date_of_birth (string): Date in YYYY-MM-DD format, e.g. '1990-01-01' "
        "- address (string): Full address, e.g. '123 Main St' ",

    "get_registration":
        "Fetches a user registration by ID or email. "
        "Input: Either a UUID string or an email address. "
        "Returns user information in JSON format.",

    "update_registration":
        "Updates an existing user registration. "
        "Input: {\"id\": \"UUID\", \"updates\": {\"field\": \"value\"}}. "
        "Only include fields you want to update in the updates object.",

    "delete_registration":
        "Deletes a user registration. "
        "Input: Either a UUID string or email address of the user to delete.",
}

# Create a single shared memory saver instance
memory = MemorySaver()

def create_agent_with_tools(tools: list):
    """
    Creates a LangChain agent that can use the provided tools.
    """
    agent = create_agent(
        model=llm,
        tools=tools,
        checkpointer=memory,
        system_prompt=(
            "You are a helpful assistant that manages user registrations.\n\n"

            "🚨 CRITICAL RULES 🚨\n"
            "1. ONLY call create_registration when you have ALL required parameters: full_name, email, phone, date_of_birth, and address.\n"
            "2. If you are missing ANY required parameter, respond conversationally asking for it. DO NOT attempt to call the tool.\n"
            "3. NEVER make up or assume parameter values.\n"
            "4. NEVER use example/default values like 'John Doe', 'john.doe@example.com', or '1234567890'.\n"
            "5. DO NOT output JSON tool calls in your response text - either call the tool properly or ask conversationally.\n"
            "6. ⚠️ NEVER claim you have information that the user hasn't explicitly provided. Only acknowledge information that was actually given.\n\n"

            "REQUIRED PARAMETERS FOR create_registration:\n"
            "- full_name (required)\n"
            "- email (required)\n"
            "- phone (required)\n"
            "- date_of_birth (required, format: YYYY-MM-DD)\n"
            "- address (optional, but ask for it)\n\n"

            "CORRECT BEHAVIOR EXAMPLES:\n\n"
            
            "Example 1 - User provides nothing:\n"
            "User: 'I want to register a new user'\n"
            "You: 'I'd be happy to help you register! To create a new user account, I'll need the following information:\n"
            "      - Full name\n"
            "      - Email address\n"
            "      - Phone number\n"
            "      - Date of birth (YYYY-MM-DD format)\n"
            "      - Address\n"
            "      Please provide these details.'\n\n"
            
            "Example 2 - User provides some info:\n"
            "User: 'Register Anu, email Anu@gmail.com, phone 9989898989'\n"
            "You: 'Great! I have:\n"
            "      ✓ Name: Anu\n"
            "      ✓ Email: Anu@gmail.com\n"
            "      ✓ Phone: 9989898989\n\n"
            "      I still need:\n"
            "      - Date of birth (YYYY-MM-DD format)\n"
            "      - Address\n"
            "      Please provide these to complete the registration.'\n\n"
            
            "Example 3 - User provides all info:\n"
            "User: 'Name: Alice Smith, email: alice@test.com, phone: 555-1234, DOB: 1990-05-15, address: 123 Main St'\n"
            "You: [Call create_registration tool with all parameters]\n\n"

            "INCORRECT BEHAVIOR (DO NOT DO THIS):\n"
            "❌ User: 'I want to register'\n"
            "❌ You: 'I have the email and phone...' (NO! User didn't provide these!)\n\n"
            "❌ You: 'I need more info. {\"name\": \"create_registration\", ...}' (NO! Don't show JSON!)\n\n"

            "ERROR HANDLING:\n"
            "- When a tool returns an error starting with 'TELL THE USER:', use that EXACT text in your response\n"
            "- DO NOT paraphrase or modify the error message\n"
            "- If email already exists, ask for a different email\n"
            "- Be patient and helpful\n\n"

            "Remember: Only acknowledge information the user has ACTUALLY provided. Never claim to have data you don't have."
        )
    )
    return agent
