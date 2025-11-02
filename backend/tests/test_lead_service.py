"""
Unit tests for lead service
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from services.lead_service import (
    generate_lead_autoresponse,
    generate_and_send_lead_autoresponse,
    score_lead
)


@pytest.fixture
def mock_db():
    """Mock database"""
    db = MagicMock()
    db["websites"] = AsyncMock()
    return db


@pytest.fixture
def sample_website():
    """Sample website data"""
    return {
        "_id": "test-website-1",
        "title": "Test Company",
        "url": "https://test.com",
        "business_type": "saas"
    }


@pytest.fixture
def sample_lead_data():
    """Sample lead data"""
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890",
        "message": "I'm interested in your product"
    }


@pytest.mark.asyncio
async def test_generate_lead_autoresponse_success(mock_db, sample_website, sample_lead_data):
    """Test successful auto-response generation"""
    mock_db["websites"].find_one = AsyncMock(return_value=sample_website)
    
    with patch('services.lead_service.LlmChat') as mock_chat:
        mock_chat_instance = AsyncMock()
        mock_chat_instance.send_message = AsyncMock(return_value="Thank you for your interest, John!")
        mock_chat.return_value.with_model.return_value = mock_chat_instance
        
        result = await generate_lead_autoresponse(mock_db, sample_lead_data, "test-website-1")
        
        assert result == "Thank you for your interest, John!"


@pytest.mark.asyncio
async def test_generate_lead_autoresponse_website_not_found(mock_db, sample_lead_data):
    """Test auto-response when website doesn't exist"""
    mock_db["websites"].find_one = AsyncMock(return_value=None)
    
    result = await generate_lead_autoresponse(mock_db, sample_lead_data, "nonexistent")
    
    assert "Thank you for your interest" in result
    assert "get back to you soon" in result


@pytest.mark.asyncio
async def test_generate_lead_autoresponse_ai_error(mock_db, sample_website, sample_lead_data):
    """Test auto-response when AI fails"""
    mock_db["websites"].find_one = AsyncMock(return_value=sample_website)
    
    with patch('services.lead_service.LlmChat') as mock_chat:
        mock_chat.return_value.with_model.return_value.send_message = AsyncMock(side_effect=Exception("API Error"))
        
        result = await generate_lead_autoresponse(mock_db, sample_lead_data, "test-website-1")
        
        # Should return fallback response
        assert "Thank you for reaching out" in result
        assert "24 hours" in result


@pytest.mark.asyncio
async def test_score_lead_hot(mock_db, sample_lead_data):
    """Test lead scoring - hot lead"""
    with patch('services.lead_service.LlmChat') as mock_chat:
        mock_chat_instance = AsyncMock()
        mock_chat_instance.send_message = AsyncMock(return_value="HOT")
        mock_chat.return_value.with_model.return_value = mock_chat_instance
        
        result = await score_lead(mock_db, sample_lead_data)
        
        assert result == "hot"


@pytest.mark.asyncio
async def test_score_lead_warm(mock_db, sample_lead_data):
    """Test lead scoring - warm lead"""
    with patch('services.lead_service.LlmChat') as mock_chat:
        mock_chat_instance = AsyncMock()
        mock_chat_instance.send_message = AsyncMock(return_value="WARM")
        mock_chat.return_value.with_model.return_value = mock_chat_instance
        
        result = await score_lead(mock_db, sample_lead_data)
        
        assert result == "warm"


@pytest.mark.asyncio
async def test_score_lead_cold(mock_db, sample_lead_data):
    """Test lead scoring - cold lead"""
    with patch('services.lead_service.LlmChat') as mock_chat:
        mock_chat_instance = AsyncMock()
        mock_chat_instance.send_message = AsyncMock(return_value="COLD")
        mock_chat.return_value.with_model.return_value = mock_chat_instance
        
        result = await score_lead(mock_db, sample_lead_data)
        
        assert result == "cold"


@pytest.mark.asyncio
async def test_score_lead_invalid_response(mock_db, sample_lead_data):
    """Test lead scoring with invalid AI response"""
    with patch('services.lead_service.LlmChat') as mock_chat:
        mock_chat_instance = AsyncMock()
        mock_chat_instance.send_message = AsyncMock(return_value="MAYBE")
        mock_chat.return_value.with_model.return_value = mock_chat_instance
        
        result = await score_lead(mock_db, sample_lead_data)
        
        # Should default to warm
        assert result == "warm"


@pytest.mark.asyncio
async def test_score_lead_error(mock_db, sample_lead_data):
    """Test lead scoring when AI fails"""
    with patch('services.lead_service.LlmChat') as mock_chat:
        mock_chat.return_value.with_model.return_value.send_message = AsyncMock(side_effect=Exception("API Error"))
        
        result = await score_lead(mock_db, sample_lead_data)
        
        # Should default to warm
        assert result == "warm"


@pytest.mark.asyncio
async def test_generate_and_send_lead_autoresponse_with_email(mock_db, sample_website, sample_lead_data):
    """Test generating and sending auto-response email"""
    mock_db["websites"].find_one = AsyncMock(return_value=sample_website)
    
    with patch('services.lead_service.LlmChat') as mock_chat, \
         patch('services.lead_service.send_lead_autoresponse_email') as mock_email:
        
        mock_chat_instance = AsyncMock()
        mock_chat_instance.send_message = AsyncMock(return_value="Thank you!")
        mock_chat.return_value.with_model.return_value = mock_chat_instance
        mock_email.return_value = True
        
        content, email_sent = await generate_and_send_lead_autoresponse(
            mock_db, sample_lead_data, "test-website-1", send_email=True
        )
        
        assert content == "Thank you!"
        assert email_sent is True
        mock_email.assert_called_once()


@pytest.mark.asyncio
async def test_generate_and_send_lead_autoresponse_without_email(mock_db, sample_website, sample_lead_data):
    """Test generating auto-response without sending email"""
    mock_db["websites"].find_one = AsyncMock(return_value=sample_website)
    
    with patch('services.lead_service.LlmChat') as mock_chat:
        mock_chat_instance = AsyncMock()
        mock_chat_instance.send_message = AsyncMock(return_value="Thank you!")
        mock_chat.return_value.with_model.return_value = mock_chat_instance
        
        content, email_sent = await generate_and_send_lead_autoresponse(
            mock_db, sample_lead_data, "test-website-1", send_email=False
        )
        
        assert content == "Thank you!"
        assert email_sent is False


@pytest.mark.asyncio
async def test_generate_and_send_lead_autoresponse_email_failure(mock_db, sample_website, sample_lead_data):
    """Test auto-response when email sending fails"""
    mock_db["websites"].find_one = AsyncMock(return_value=sample_website)
    
    with patch('services.lead_service.LlmChat') as mock_chat, \
         patch('services.lead_service.send_lead_autoresponse_email') as mock_email:
        
        mock_chat_instance = AsyncMock()
        mock_chat_instance.send_message = AsyncMock(return_value="Thank you!")
        mock_chat.return_value.with_model.return_value = mock_chat_instance
        
        from services.email_service import EmailDeliveryError
        mock_email.side_effect = EmailDeliveryError("SMTP error")
        
        content, email_sent = await generate_and_send_lead_autoresponse(
            mock_db, sample_lead_data, "test-website-1", send_email=True
        )
        
        assert content == "Thank you!"
        assert email_sent is False  # Email failed but content was generated
