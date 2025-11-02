"""
Unit tests for chatbot service
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from services.chatbot_service import process_chatbot_message, get_chatbot_history


@pytest.fixture
def mock_db():
    """Mock database"""
    db = MagicMock()
    db["chatbot_messages"] = AsyncMock()
    db["chatbot_sessions"] = AsyncMock()
    db["websites"] = AsyncMock()
    return db


@pytest.fixture
def sample_website():
    """Sample website data"""
    return {
        "_id": "test-website-1",
        "title": "Test Company",
        "url": "https://test.com",
        "business_type": "saas",
        "content_digest": "We provide SaaS solutions"
    }


@pytest.mark.asyncio
async def test_process_chatbot_message_success(mock_db, sample_website):
    """Test successful chatbot message processing"""
    # Setup mocks
    mock_db["websites"].find_one = AsyncMock(return_value=sample_website)
    mock_db["chatbot_sessions"].find_one = AsyncMock(return_value=None)
    mock_db["chatbot_sessions"].insert_one = AsyncMock()
    mock_db["chatbot_messages"].insert_one = AsyncMock()
    mock_db["chatbot_messages"].find = MagicMock()
    mock_db["chatbot_messages"].find.return_value.sort = MagicMock()
    mock_db["chatbot_messages"].find.return_value.sort.return_value.limit = MagicMock()
    mock_db["chatbot_messages"].find.return_value.sort.return_value.limit.return_value.to_list = AsyncMock(return_value=[])
    mock_db["chatbot_sessions"].update_one = AsyncMock()
    
    # Mock AI response
    with patch('services.chatbot_service.LlmChat') as mock_chat:
        mock_chat_instance = AsyncMock()
        mock_chat_instance.send_message = AsyncMock(return_value="Hello! How can I help you?")
        mock_chat.return_value.with_model.return_value = mock_chat_instance
        
        result = await process_chatbot_message(
            db=mock_db,
            website_id="test-website-1",
            session_id="test-session-1",
            message="Hello"
        )
        
        assert "response" in result
        assert result["response"] == "Hello! How can I help you?"
        assert "session_id" in result
        assert result["session_id"] == "test-session-1"


@pytest.mark.asyncio
async def test_process_chatbot_message_website_not_found(mock_db):
    """Test chatbot message when website doesn't exist"""
    mock_db["websites"].find_one = AsyncMock(return_value=None)
    
    result = await process_chatbot_message(
        db=mock_db,
        website_id="nonexistent",
        session_id="test-session",
        message="Hello"
    )
    
    assert "error" in result
    assert result["error"] == "Website not found"


@pytest.mark.asyncio
async def test_process_chatbot_message_ai_error(mock_db, sample_website):
    """Test chatbot message when AI service fails"""
    mock_db["websites"].find_one = AsyncMock(return_value=sample_website)
    mock_db["chatbot_sessions"].find_one = AsyncMock(return_value=None)
    mock_db["chatbot_sessions"].insert_one = AsyncMock()
    mock_db["chatbot_messages"].insert_one = AsyncMock()
    mock_db["chatbot_messages"].find = MagicMock()
    mock_db["chatbot_messages"].find.return_value.sort = MagicMock()
    mock_db["chatbot_messages"].find.return_value.sort.return_value.limit = MagicMock()
    mock_db["chatbot_messages"].find.return_value.sort.return_value.limit.return_value.to_list = AsyncMock(return_value=[])
    
    # Mock AI failure
    with patch('services.chatbot_service.LlmChat') as mock_chat:
        mock_chat.return_value.with_model.return_value.send_message = AsyncMock(side_effect=Exception("API Error"))
        
        result = await process_chatbot_message(
            db=mock_db,
            website_id="test-website-1",
            session_id="test-session-1",
            message="Hello"
        )
        
        # Should return fallback response
        assert "response" in result
        assert "trouble processing" in result["response"].lower()
        assert "error" in result


@pytest.mark.asyncio
async def test_get_chatbot_history(mock_db):
    """Test retrieving chatbot history"""
    mock_messages = [
        {"_id": "1", "role": "user", "content": "Hello", "timestamp": datetime.now(timezone.utc)},
        {"_id": "2", "role": "assistant", "content": "Hi there!", "timestamp": datetime.now(timezone.utc)}
    ]
    
    mock_db["chatbot_messages"].find = MagicMock()
    mock_db["chatbot_messages"].find.return_value.sort = MagicMock()
    mock_db["chatbot_messages"].find.return_value.sort.return_value.limit = MagicMock()
    mock_db["chatbot_messages"].find.return_value.sort.return_value.limit.return_value.to_list = AsyncMock(return_value=mock_messages)
    
    result = await get_chatbot_history(mock_db, "test-session-1", limit=50)
    
    assert len(result) == 2
    assert result[0]["role"] == "user"
    assert result[1]["role"] == "assistant"


@pytest.mark.asyncio
async def test_process_chatbot_message_user_only(mock_db, sample_website):
    """Test storing user message only without AI response"""
    mock_db["websites"].find_one = AsyncMock(return_value=sample_website)
    mock_db["chatbot_sessions"].find_one = AsyncMock(return_value={"_id": "existing-session"})
    mock_db["chatbot_messages"].insert_one = AsyncMock()
    
    result = await process_chatbot_message(
        db=mock_db,
        website_id="test-website-1",
        session_id="test-session-1",
        message="Hello",
        user_message_only=True
    )
    
    assert "message_id" in result
    assert "response" not in result
