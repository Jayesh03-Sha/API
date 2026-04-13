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
        """Authenticate against the DIC / DIN motor policy API."""
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
        """Generate motor quote using the DIN quote API."""
        if not self.token:
            self.authenticate()

        headers = {
            "Authorization": f"Bearer {self.token}",
            "X-REQUEST-ID": data.get('request_id', "UUID-MOCK-123")
        }

        payload = {
            "insuredName": {
                "en": data.get('insured_name_en', data.get('insured_name', 'Test User')),
                "ar": data.get('insured_name_ar', data.get('insured_name', 'Test User'))
            },
            "nationality": str(data.get('nationality', data.get('nationality_code', '101'))),
            "nationalId": data.get('national_id', data.get('nid', '35363735322')),
            "idExpiryDt": data.get('id_expiry_dt', data.get('idExpiryDt', '21/10/2038')),
            "dateOfBirth": data.get('date_of_birth', data.get('dob', '14/10/1997')),
            "gender": data.get('gender', 'F'),
            "emirate": data.get('emirate', data.get('emirates_id', '03')),
            "emailAddress": data.get('email', data.get('emailAddress', 'test@example.com')),
            "mobileNumber": data.get('mobile_number', data.get('mobileNumber', '97135687632')),
            "licenseNo": data.get('license_no', data.get('licenseNo', '35372179989')),
            "licenseFmDt": data.get('license_from_date', data.get('licenseFmDt', '21/05/2017')),
            "licenseToDt": data.get('license_to_date', data.get('licenseToDt', '28/11/2038')),
            "chassisNumber": data.get('chassis_number', data.get('VehChassisNo', 'JTJHY00W0J4282051')),
            "regNumber": data.get('reg_number', data.get('regNumber', '6562')),
            "regDt": data.get('reg_dt', data.get('regDt', '17/07/2020')),
            "plateCode": data.get('plate_code', data.get('plateCode', 'E')),
            "plateSource": data.get('plate_source', data.get('plateSource', '0001')),
            "tcfNumber": data.get('tcf_number', data.get('tcfNumber', '343')),
            "ncdYears": data.get('ncd_years', data.get('ncdYears', '2')),
            "trafficTranType": data.get('traffic_tran_type', data.get('trafficTranType', '101')),
            "isVehBrandNew": data.get('is_vehicle_brand_new', data.get('isVehBrandNew', 'N')),
            "agencyRepairYn": data.get('agency_repair_yn', data.get('agencyRepairYn', 'N')),
            "bankName": data.get('bank_name', data.get('bankName', '192')),
            "documentLists": data.get('documentLists', data.get('document_lists', []))
        }

        response, response_time = self._make_request(
            method="POST",
            endpoint="api/v1/Insurance/GenerateQuote",
            headers=headers,
            json=payload
        )

        quote_list = []
        if response:
            if isinstance(response, dict) and 'data' in response:
                quote_list = response.get('data') or []
            elif isinstance(response, list):
                quote_list = response

        if not quote_list:
            return None

        normalized_quotes = []
        for item in quote_list:
            normalized = self.normalize(item)
            normalized['provider_id'] = 'dic_broker_uae'
            normalized['response_time_ms'] = response_time
            normalized_quotes.append(normalized)

        return normalized_quotes[0]

    def choose_scheme(self, prod_code: str, covers: Dict = None) -> Optional[Dict]:
        """Select a scheme and calculate tariff for the chosen plan."""
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

        if response and isinstance(response, dict) and response.get('data'):
            return response.get('data')
        return response

    def get_policy(self, quotation_no: str) -> Optional[Dict]:
        """Retrieve policy/payment status for a completed quotation."""
        if not self.token:
            self.authenticate()

        response, _ = self._make_request(
            method="GET",
            endpoint=f"api/v1/Insurance/GetPaymentInfo?quotationNo={quotation_no}",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        if response and isinstance(response, dict) and response.get('data'):
            return response.get('data')
        return response

    def normalize(self, response_data: Dict) -> Dict:
        """Normalize DIN/DIC quote response for comparison."""
        product_name = response_data.get('prodName')
        if isinstance(product_name, dict):
            product_name = product_name.get('en') or product_name.get('ar')

        covers = response_data.get('covers', {}) or {}
        mandatory = covers.get('mandatory') or []
        optional = covers.get('optional') or []

        return {
            'provider': self.provider_name,
            'prod_code': response_data.get('prodCode'),
            'plan_name': product_name,
            'premium': float(response_data.get('premium', 0)) if response_data.get('premium') is not None else float(response_data.get('grossPremium', 0) or 0),
            'coverage': float(response_data.get('sumInsured', 0)) if response_data.get('sumInsured') is not None else 0.0,
            'benefits': mandatory + optional,
            'mandatory_covers': mandatory,
            'optional_covers': optional,
        }
