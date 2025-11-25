
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_db
from app.tools.registration_tools import RegistrationTools
from langchain_core.tools import StructuredTool
from app.agents.langchain_agent import create_agent_with_tools

router = APIRouter(prefix="/chat", tags=["Chat"])

SESSIONS = {}

class ChatMessage(BaseModel):
    message: str


class CreateRegistrationInput(BaseModel):
    """Input schema for creating a new user registration. ALL fields are required."""
    full_name: str = Field(..., description="User's REAL full name (required)")
    email: str = Field(..., description="User's REAL email address (required)")
    phone: str = Field(..., description="User's REAL phone number (required)")
    date_of_birth: str = Field(..., description="User's date of birth in YYYY-MM-DD format (required)")
    address: str = Field("", description="User's address (optional, can be empty string)")

class GetRegistrationInput(BaseModel):
    """Input schema for getting a user by email or ID."""
    identifier: str = Field(..., description="User's email or UUID (required)")

class UpdateRegistrationInput(BaseModel):
    """Input schema for updating a user."""
    user_id: str = Field(..., description="User's UUID or email (required)")
    full_name: Optional[str] = Field(None, description="Updated full name (optional)")
    email: Optional[str] = Field(None, description="Updated email (optional)")
    phone: Optional[str] = Field(None, description="Updated phone (optional)")
    date_of_birth: Optional[str] = Field(None, description="Updated date of birth (optional)")
    address: Optional[str] = Field(None, description="Updated address (optional)")

class DeleteRegistrationInput(BaseModel):
    """Input schema for deleting a user."""
    identifier: str = Field(..., description="User's email or UUID to delete (required)")


@router.post("/{session_id}")
def chat(session_id: str, body: ChatMessage, db: Session = Depends(get_db)):
    user_msg = body.message.strip()

    if session_id not in SESSIONS:
        SESSIONS[session_id] = {"history": []}

    reg_tools = RegistrationTools(db)

    def create_wrapper(full_name: str, email: str, phone: str, date_of_birth: str, address: str = "") -> str:
        import json
        data = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "date_of_birth": date_of_birth,
            "address": address
        }
        return reg_tools.create(data)

    def get_wrapper(identifier: str) -> str:
        return reg_tools.get(identifier)

    def update_wrapper(user_id: str, full_name: Optional[str] = None, email: Optional[str] = None,
                       phone: Optional[str] = None, date_of_birth: Optional[str] = None,
                       address: Optional[str] = None) -> str:
        import json

        user = reg_tools._resolve_registration(user_id)
        if not user:
            return json.dumps({"error": f"User not found with identifier: {user_id}. Please provide a valid email or user ID."})

        updates = {}
        if full_name: updates["full_name"] = full_name
        if email: updates["email"] = email
        if phone: updates["phone"] = phone
        if date_of_birth: updates["date_of_birth"] = date_of_birth
        if address: updates["address"] = address

        if not updates:
            return json.dumps({"error": "No fields to update. Please specify what you want to change."})

        data = {"id": str(user.id), "updates": updates}
        return reg_tools.update(data)

    def delete_wrapper(identifier: str) -> str:
        return reg_tools.delete(identifier)

    tools = [
        StructuredTool.from_function(
            func=create_wrapper,
            name="create_registration",
            description="Creates a new user registration. ALL fields are required.",
            args_schema=CreateRegistrationInput
        ),
        StructuredTool.from_function(
            func=get_wrapper,
            name="get_registration",
            description="Gets a user by email or UUID",
            args_schema=GetRegistrationInput
        ),
        StructuredTool.from_function(
            func=update_wrapper,
            name="update_registration",
            description="Updates a user's information",
            args_schema=UpdateRegistrationInput
        ),
        StructuredTool.from_function(
            func=delete_wrapper,
            name="delete_registration",
            description="Deletes a user by email or UUID",
            args_schema=DeleteRegistrationInput
        ),
    ]

    agent = create_agent_with_tools(tools)

    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_msg}]},
        config={"configurable": {"thread_id": session_id}}
    )

    messages = result.get("messages", [])
    if messages:
        for msg in reversed(messages):
            if hasattr(msg, 'content') and msg.content:
                has_tool_calls = hasattr(msg, 'tool_calls') and msg.tool_calls
                if not has_tool_calls:
                    reply = msg.content
                    break
        else:
            reply = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
    else:
        reply = "No response"

    SESSIONS[session_id]["history"].append({"user": user_msg, "bot": reply})

    return {"reply": reply}
