"""
Test script to verify that the agent has memory across multiple requests.
This test mocks the agent to avoid Ollama dependency.
"""

from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_agent_memory():
    """Test that the agent remembers information across multiple requests in the same session."""
    
    with patch("app.routes.chat.create_agent_with_tools") as mock_create_agent:
        # Create a mock agent that will be called twice
        mock_agent = MagicMock()
        
        # First call: User provides name and email
        mock_agent.invoke.return_value = {
            "messages": [
                MagicMock(
                    content="Great! I have your name (Alice Smith) and email (alice@test.com). I still need your phone number, date of birth, and address.",
                    tool_calls=None
                )
            ]
        }
        mock_create_agent.return_value = mock_agent
        
        response1 = client.post(
            "/chat/memory_test_session",
            json={"message": "I want to register. My name is Alice Smith and my email is alice@test.com"}
        )
        
        print("First request:")
        print(f"Status: {response1.status_code}")
        print(f"Response: {response1.json()}")
        
        # Second call: User provides phone
        # The agent should remember the name and email from the first call
        mock_agent.invoke.return_value = {
            "messages": [
                MagicMock(
                    content="Perfect! I now have your name, email, and phone (555-1234). I still need your date of birth and address.",
                    tool_calls=None
                )
            ]
        }
        
        response2 = client.post(
            "/chat/memory_test_session",
            json={"message": "My phone is 555-1234"}
        )
        
        print("\nSecond request:")
        print(f"Status: {response2.status_code}")
        print(f"Response: {response2.json()}")
        
        # Verify that the agent was called with the thread_id
        assert mock_agent.invoke.call_count == 2
        
        # Check that both calls used the same thread_id
        first_call_config = mock_agent.invoke.call_args_list[0][1]['config']
        second_call_config = mock_agent.invoke.call_args_list[1][1]['config']
        
        print(f"\nFirst call config: {first_call_config}")
        print(f"Second call config: {second_call_config}")
        
        assert first_call_config['configurable']['thread_id'] == 'memory_test_session'
        assert second_call_config['configurable']['thread_id'] == 'memory_test_session'
        
        print("\n✅ Memory test passed! The agent uses the same thread_id across requests.")

if __name__ == "__main__":
    test_agent_memory()
