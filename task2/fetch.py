"""
Fetch module: Extracts data from the CoinGecko API with robust error handling.
"""
import logging
from typing import Any

import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryError
)

from config import config

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, config.log_level.upper()),
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "event": "%(event)s", "message": "%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%S"
)
logger = logging.getLogger(__name__)


class APIError(Exception):
    """Custom exception for API errors."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limit is hit (HTTP 429)."""
    pass


class ClientError(APIError):
    """Raised for 4xx client errors (should not retry)."""
    pass


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    retry=retry_if_exception_type((requests.exceptions.RequestException, RateLimitError)),
    reraise=True
)
def fetch_page(page: int) -> list[dict[str, Any]]:
    """
    Fetch a single page of coin market data from CoinGecko.
    
    Args:
        page: Page number (1-indexed)
    
    Returns:
        List of coin data dictionaries
    
    Raises:
        ClientError: For 4xx errors (URL/params wrong, do not retry)
        RateLimitError: For 429 errors (will retry with backoff)
        APIError: For 5xx server errors (will retry)
    """
    params = {
        "vs_currency": config.coingecko_vs_currency,
        "order": "market_cap_desc",
        "per_page": config.coingecko_per_page,
        "page": page,
        "sparkline": "false",
        "price_change_percentage": "24h,7d"
    }
    
    logger.info(
        f"Fetching page {page}",
        extra={"event": "api_fetch_start", "page": page}
    )
    
    try:
        response = requests.get(
            config.coingecko_api_endpoint,
            params=params,
            timeout=(5, 30)
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(
                f"Successfully fetched {len(data)} coins from page {page}",
                extra={"event": "api_fetch_success", "page": page, "rows": len(data)}
            )
            return data
        
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            error_msg = f"Rate limited (429). Retry-After: {retry_after}s"
            logger.warning(
                error_msg,
                extra={"event": "api_rate_limit", "page": page, "retry_after": retry_after}
            )
            raise RateLimitError(error_msg)
        
        elif 400 <= response.status_code < 500:
            error_msg = f"Client error {response.status_code}: {response.text}"
            logger.error(
                error_msg,
                extra={"event": "api_client_error", "page": page, "status": response.status_code}
            )
            raise ClientError(error_msg)
        
        else:
            error_msg = f"Server error {response.status_code}: {response.text}"
            logger.error(
                error_msg,
                extra={"event": "api_server_error", "page": page, "status": response.status_code}
            )
            raise APIError(error_msg)
    
    except requests.exceptions.Timeout as e:
        logger.error(
            f"Request timeout: {e}",
            extra={"event": "api_timeout", "page": page}
        )
        raise
    
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Request failed: {e}",
            extra={"event": "api_request_error", "page": page}
        )
        raise


def fetch_all_pages() -> list[dict[str, Any]]:
    """
    Fetch all pages of coin market data up to max_pages.
    
    Returns:
        List of all coin data dictionaries across all pages
    """
    all_data = []
    
    for page in range(1, config.coingecko_max_pages + 1):
        try:
            page_data = fetch_page(page)
            
            if not page_data:
                logger.info(
                    f"No more data on page {page}, stopping pagination",
                    extra={"event": "api_pagination_end", "page": page}
                )
                break
            
            all_data.extend(page_data)
            
        except ClientError:
            logger.error("Client error encountered, stopping pipeline")
            raise
        
        except RetryError as e:
            logger.error(
                f"Max retries exceeded for page {page}: {e}",
                extra={"event": "api_max_retries", "page": page}
            )
            raise APIError(f"Failed to fetch page {page} after max retries") from e
    
    logger.info(
        f"Total coins fetched: {len(all_data)}",
        extra={"event": "fetch_complete", "total_rows": len(all_data)}
    )
    
    return all_data
