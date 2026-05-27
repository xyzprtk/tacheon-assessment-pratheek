"""
Unit tests for the fetch module.
"""
import pytest
from unittest.mock import Mock, patch
from fetch import fetch_page, RateLimitError, ClientError, APIError


@pytest.fixture
def mock_response():
    """Create a mock response object."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = [
        {"id": "bitcoin", "symbol": "btc", "name": "Bitcoin", "current_price": 50000.0}
    ]
    response.headers = {}
    response.text = ""
    return response


def test_fetch_page_success(mock_response):
    """Test successful API fetch."""
    with patch('fetch.requests.get', return_value=mock_response) as mock_get:
        data = fetch_page(1)
        
        assert len(data) == 1
        assert data[0]["id"] == "bitcoin"
        mock_get.assert_called_once()


def test_fetch_page_rate_limit():
    """Test rate limit handling."""
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.headers = {"Retry-After": "60"}
    mock_response.text = "Rate limited"
    
    with patch('fetch.requests.get', return_value=mock_response):
        with pytest.raises(RateLimitError):
            fetch_page(1)


def test_fetch_page_client_error():
    """Test client error handling."""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad request"
    
    with patch('fetch.requests.get', return_value=mock_response):
        with pytest.raises(ClientError):
            fetch_page(1)


def test_fetch_page_server_error():
    """Test server error handling."""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal server error"
    
    with patch('fetch.requests.get', return_value=mock_response):
        with pytest.raises(APIError):
            fetch_page(1)
