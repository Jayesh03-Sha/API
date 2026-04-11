from typing import Optional, Dict
from .base import BaseProvider


class DICProvider(BaseProvider):
    def __init__(self, api_key: str = None, base_url: str = None):
        super().__init__(
            api_key=api_key or 'dic_uae_test_key_001',
            base_url=base_url or 'http://localhost:8000/mock-api/'
        )
        self.provider_name = 'DIC Insurance Broker UAE'
        self.token = None
        self.token_expiry = None

    def authenticate(self):
        """Standard Authentication API for DIN/DIC"""
        payload = {
            "userName": "MOTOR_USER_001",
            "password": "123456"
        }
        response, _ = self._make_request(
            method="POST",
            endpoint="api/v1/User/Auth",
            json=payload
        )
        if response and response.get('status') == 1:
            self.token = response.get('data')
            return self.token
        return None

    def get_quote(self, data: Dict) -> Optional[Dict]:
        """Generate Quote API (Core Engine)"""
        if not self.token:
            self.authenticate()

        headers = {
            "Authorization": f"Bearer {self.token}",
            "X-REQUEST-ID": data.get('request_id', "UUID-MOCK-123")
        }

        # Structured request per documentation
        payload = {
            "personal_info": {
                "emirates_id": data.get('nid') or "784-1990-1234567-1",
                "dob": data.get('dob'),
                "gender": data.get('gender')
            },
            "vehicle_info": {
                "chassis_number": data.get('chassis_number'),
                "reg_number": data.get('reg_number'),
                "make": data.get('make'),
                "model": data.get('model'),
                "year": data.get('year')
            }
        }

        response, response_time = self._make_request(
            method="POST",
            endpoint="api/v1/Insurance/GenerateQuote",
            headers=headers,
            json=payload
        )

        if response and isinstance(response, list):
            # Normalize multiple products
            normalized_quotes = []
            for item in response:
                norm = self.normalize(item)
                norm['provider_id'] = 'dic_broker_uae'
                norm['response_time_ms'] = response_time
                normalized_quotes.append(norm)
            
            # For back-compatibility with current aggregator which expects a single quote
            return normalized_quotes[0] if normalized_quotes else None

        return None

    def choose_scheme(self, prod_code: str, covers: Dict = None) -> Optional[Dict]:
        """Select Scheme API"""
        if not self.token:
            self.authenticate()

        payload = {
            "prodCode": prod_code,
            "covers": covers or {"mandatory": "", "optional": ""}
        }
        
        response, _ = self._make_request(
            method="POST",
            endpoint="api/v1/Insurance/ChooseScheme",
            headers={"Authorization": f"Bearer {self.token}"},
            json=payload
        )
        return response

    def get_policy(self, quotation_no: str) -> Optional[Dict]:
        """Get Policy / Payment Info API"""
        if not self.token:
            self.authenticate()

        response, _ = self._make_request(
            method="GET",
            endpoint=f"api/v1/Insurance/GetPaymentInfo?quotationNo={quotation_no}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        return response

    def normalize(self, response_data: Dict) -> Dict:
        """Normalized response for UI comparison"""
        return {
            'provider': self.provider_name,
            'prod_code': response_data.get('prodCode'),
            'plan_name': response_data.get('prodName'),
            'premium': float(response_data.get('premium', 0)) or 1100.0, # fallback mockup
            'coverage': float(response_data.get('sumInsured', 0)),
            'benefits': response_data.get('covers', {}).get('mandatory', []) + 
                        response_data.get('covers', {}).get('optional', []),
            'mandatory_covers': response_data.get('covers', {}).get('mandatory', []),
            'optional_covers': response_data.get('covers', {}).get('optional', []),
        }