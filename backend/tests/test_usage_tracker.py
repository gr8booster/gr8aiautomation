"""
Unit tests for usage tracker service
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from services.usage_tracker import (
    PLAN_LIMITS,
    track_usage,
    get_usage,
    check_limit
)


@pytest.fixture
def mock_db():
    """Mock database"""
    db = MagicMock()
    db["usage"] = AsyncMock()
    db["websites"] = AsyncMock()
    db["active_automations"] = AsyncMock()
    return db


def test_plan_limits():
    """Test plan limits are defined correctly"""
    assert "free" in PLAN_LIMITS
    assert "starter" in PLAN_LIMITS
    assert "pro" in PLAN_LIMITS
    
    # Free plan
    assert PLAN_LIMITS["free"]["websites"] == 1
    assert PLAN_LIMITS["free"]["automations"] == 3
    assert PLAN_LIMITS["free"]["ai_interactions"] == 100
    assert PLAN_LIMITS["free"]["price"] == 0
    
    # Starter plan
    assert PLAN_LIMITS["starter"]["websites"] == 3
    assert PLAN_LIMITS["starter"]["automations"] == 10
    assert PLAN_LIMITS["starter"]["ai_interactions"] == 1000
    assert PLAN_LIMITS["starter"]["price"] == 29.0
    
    # Pro plan
    assert PLAN_LIMITS["pro"]["websites"] == 10
    assert PLAN_LIMITS["pro"]["automations"] == 9999
    assert PLAN_LIMITS["pro"]["ai_interactions"] == 10000
    assert PLAN_LIMITS["pro"]["price"] == 99.0


@pytest.mark.asyncio
async def test_track_usage_new_record(mock_db):
    """Test tracking usage creates new record"""
    mock_db["usage"].update_one = AsyncMock()
    
    await track_usage(mock_db, "user-1", ai_interactions=5, chatbot_messages=10)
    
    mock_db["usage"].update_one.assert_called_once()
    call_args = mock_db["usage"].update_one.call_args
    
    # Check query
    assert call_args[0][0]["user_id"] == "user-1"
    assert "month" in call_args[0][0]
    
    # Check update
    assert call_args[0][1]["$inc"]["ai_interactions"] == 5
    assert call_args[0][1]["$inc"]["chatbot_messages"] == 10
    
    # Check upsert
    assert call_args[1]["upsert"] is True


@pytest.mark.asyncio
async def test_get_usage_existing(mock_db):
    """Test getting existing usage"""
    mock_usage = {
        "user_id": "user-1",
        "month": "2024-01",
        "ai_interactions": 50,
        "chatbot_messages": 200
    }
    mock_db["usage"].find_one = AsyncMock(return_value=mock_usage)
    
    result = await get_usage(mock_db, "user-1")
    
    assert result["ai_interactions"] == 50
    assert result["chatbot_messages"] == 200


@pytest.mark.asyncio
async def test_get_usage_not_found(mock_db):
    """Test getting usage when none exists"""
    mock_db["usage"].find_one = AsyncMock(return_value=None)
    
    result = await get_usage(mock_db, "user-1")
    
    assert result["ai_interactions"] == 0
    assert result["chatbot_messages"] == 0


@pytest.mark.asyncio
async def test_check_limit_ai_interactions_within_limit(mock_db):
    """Test AI interactions within limit"""
    mock_usage = {
        "ai_interactions": 50,
        "chatbot_messages": 100
    }
    mock_db["usage"].find_one = AsyncMock(return_value=mock_usage)
    
    result = await check_limit(mock_db, "user-1", "ai_interactions", "free")
    
    assert result is True  # 50 < 100 (free plan limit)


@pytest.mark.asyncio
async def test_check_limit_ai_interactions_exceeded(mock_db):
    """Test AI interactions exceeded"""
    mock_usage = {
        "ai_interactions": 100,
        "chatbot_messages": 100
    }
    mock_db["usage"].find_one = AsyncMock(return_value=mock_usage)
    
    result = await check_limit(mock_db, "user-1", "ai_interactions", "free")
    
    assert result is False  # 100 >= 100 (free plan limit)


@pytest.mark.asyncio
async def test_check_limit_websites_within_limit(mock_db):
    """Test websites within limit"""
    mock_db["websites"].count_documents = AsyncMock(return_value=0)
    
    result = await check_limit(mock_db, "user-1", "websites", "free")
    
    assert result is True  # 0 < 1 (free plan limit)


@pytest.mark.asyncio
async def test_check_limit_websites_exceeded(mock_db):
    """Test websites exceeded"""
    mock_db["websites"].count_documents = AsyncMock(return_value=1)
    
    result = await check_limit(mock_db, "user-1", "websites", "free")
    
    assert result is False  # 1 >= 1 (free plan limit)


@pytest.mark.asyncio
async def test_check_limit_automations_within_limit(mock_db):
    """Test automations within limit"""
    mock_db["active_automations"].count_documents = AsyncMock(return_value=2)
    
    result = await check_limit(mock_db, "user-1", "automations", "free")
    
    assert result is True  # 2 < 3 (free plan limit)


@pytest.mark.asyncio
async def test_check_limit_automations_exceeded(mock_db):
    """Test automations exceeded"""
    mock_db["active_automations"].count_documents = AsyncMock(return_value=3)
    
    result = await check_limit(mock_db, "user-1", "automations", "free")
    
    assert result is False  # 3 >= 3 (free plan limit)


@pytest.mark.asyncio
async def test_check_limit_pro_plan(mock_db):
    """Test pro plan has higher limits"""
    mock_usage = {
        "ai_interactions": 5000,
        "chatbot_messages": 1000
    }
    mock_db["usage"].find_one = AsyncMock(return_value=mock_usage)
    
    result = await check_limit(mock_db, "user-1", "ai_interactions", "pro")
    
    assert result is True  # 5000 < 10000 (pro plan limit)


@pytest.mark.asyncio
async def test_check_limit_unknown_type(mock_db):
    """Test unknown limit type returns True"""
    result = await check_limit(mock_db, "user-1", "unknown_type", "free")
    
    assert result is True  # Unknown types allow access
