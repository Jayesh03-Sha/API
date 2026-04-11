from abc import ABC, abstractmethod
from typing import Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """Abstract base class for all insurance providers"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url
        self.provider_name = None
        self.timeout = 10  # seconds
        self.api_logger = logging.getLogger('api_providers')
    
    @abstractmethod
    def get_quote(self, data: Dict) -> Optional[Dict]:
        """
        Get a quote from the provider.
        
        Args:
            data: Dictionary containing quote parameters
            
        Returns:
            Normalized quote dictionary or None if failed
        """
        pass
    
    @abstractmethod
    def normalize(self, response_data: Dict) -> Dict:
        """
        Normalize provider API response to standard format.
        
        Args:
            response_data: Raw response from provider API
            
        Returns:
            Standardized quote dictionary
        """
        pass
    
    def _make_request(self, method: str = 'POST', endpoint: str = '', **kwargs) -> Optional[Dict]:
        """
        Make HTTP request to provider API.
        
        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint (relative to base_url)
            **kwargs: Additional requests parameters
            
        Returns:
            JSON response or None if request failed
        """
        import requests
        import urllib.parse
        
        # Combine base_url and endpoint
        url = urllib.parse.urljoin(self.base_url, endpoint) if self.base_url else endpoint
        
        try:
            start_time = time.time()
            
            headers = kwargs.pop('headers', {})
            if self.api_key:
                # Some APIs use Authorization header directly with token
                if not headers.get('Authorization'):
                    headers['Authorization'] = f'Bearer {self.api_key}'
            
            json_payload = kwargs.get('json', {})
            params = kwargs.get('params', {})

            self.api_logger.debug(
                f"REQUEST | Provider: {self.provider_name} | Method: {method} | URL: {url}\n"
                f"HEADERS: {headers}\n"
                f"PAYLOAD: {json_payload or params}"
            )

            if method.upper() == 'POST':
                response = requests.post(
                    url,
                    headers=headers,
                    timeout=self.timeout,
                    **kwargs
                )
            else:
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=self.timeout,
                    **kwargs
                )
            
            response_time = int((time.time() - start_time) * 1000)  # ms
            
            # Log response
            self.api_logger.debug(
                f"RESPONSE | Provider: {self.provider_name} | Status: {response.status_code} | Time: {response_time}ms\n"
                f"BODY: {response.text[:1000]}{'...' if len(response.text) > 1000 else ''}"
            )

            if response.status_code == 200:
                try:
                    return response.json(), response_time
                except Exception:
                    # Return raw content if not JSON
                    return {"raw_response": response.text}, response_time
            else:
                logger.warning(
                    f"{self.provider_name} API error: {response.status_code} - {response.text}"
                )
                return None, response_time
                
        except requests.exceptions.Timeout:
            logger.error(f"{self.provider_name} request timeout")
            return None, self.timeout * 1000
        except requests.exceptions.ConnectionError:
            logger.error(f"{self.provider_name} connection error")
            return None, 0
        except Exception as e:
            logger.error(f"{self.provider_name} error: {str(e)}")
            return None, 0
