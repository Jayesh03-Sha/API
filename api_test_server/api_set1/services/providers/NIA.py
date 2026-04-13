from typing import Optional, Dict, List
from .base import BaseProvider


class NIAProvider(BaseProvider):
    """NIA Motor Insurance Provider integration"""

    def __init__(self, api_key: str = None, base_url: str = None):
        super().__init__(
            api_key=api_key or 'nia_uae_test_key_003',
            base_url=base_url or 'http://localhost:8000/mock-api/nia/'
        )
        self.provider_name = 'NIA Insurance UAE'
        self.token = None

    def authenticate(self) -> Optional[str]:
        """Authenticate with NIA and obtain a session token."""
        payload = {
            "username": "sabir.a@nia-dubai.com",
            "password": "123456",
            "loginMode": "EMAIL"
        }
        response, _ = self._make_request(
            method="POST",
            endpoint="Api/Auth/Login",
            json=payload
        )
        if response and response.get('Status') == 1:
            token = response.get('Data')
            self.token = token
            return token
        return None

    def get_quote(self, data: Dict) -> Optional[Dict]:
        """Create a motor quotation and return the normalized best quote."""
        if not self.token:
            self.authenticate()

        headers = {
            "Authorization": f"Bearer {self.token}" if self.token else "",
            "Content-Type": "application/json"
        }
        payload = self._build_create_quote_payload(data)

        response, response_time = self._make_request(
            method="POST",
            endpoint="Api/Motor/CreateQuote",
            headers=headers,
            json=payload
        )

        if response and response.get('Status') == 1:
            quote_data = response.get('Data', {})
            normalized = self.normalize(quote_data)
            normalized['provider_id'] = 'nia_uae'
            normalized['response_time_ms'] = response_time
            return normalized
        return None

    def save_quote_with_plan(self, reference_no: str, scheme_code: str, product_code: str, selected_covers: List[Dict]) -> Optional[Dict]:
        """Save the selected plan and covers for a quotation."""
        payload = {
            "ReferenceNo": reference_no,
            "SchemeCode": scheme_code,
            "ProductCode": product_code,
            "SelectedCovers": selected_covers
        }
        headers = self._auth_headers()
        response, _ = self._make_request(
            method="POST",
            endpoint="Api/Motor/SaveQuoteWithPlan",
            headers=headers,
            json=payload
        )
        return response

    def save_additional_info(self, reference_no: str, additional_info: Dict) -> Optional[Dict]:
        """Save additional policy information after plan selection."""
        payload = {"PolRefNo": reference_no, **additional_info}
        headers = self._auth_headers()
        response, _ = self._make_request(
            method="POST",
            endpoint="Api/Motor/SaveAddlInfo",
            headers=headers,
            json=payload
        )
        return response

    def save_document(self, reference_no: str, documents: List[Dict]) -> Optional[Dict]:
        """Upload documents as base64 to the NIA portal."""
        payload = {
            "polRefNo": reference_no,
            "docUpload": documents
        }
        headers = self._auth_headers()
        response, _ = self._make_request(
            method="POST",
            endpoint="Api/Motor/SaveDocument",
            headers=headers,
            json=payload
        )
        return response

    def proposal_summary(self, reference_no: str) -> Optional[Dict]:
        """Fetch proposal / policy summary for a quotation."""
        payload = {"PolRefNo": reference_no}
        headers = self._auth_headers()
        response, _ = self._make_request(
            method="POST",
            endpoint="Api/Motor/ProposalSummary",
            headers=headers,
            json=payload
        )
        return response

    def approve_policy(self, reference_no: str, pay_type: str = "OA") -> Optional[Dict]:
        """Approve the policy and generate the final policy number."""
        payload = {
            "PolRefNo": reference_no,
            "PayType": pay_type
        }
        headers = self._auth_headers()
        response, _ = self._make_request(
            method="POST",
            endpoint="Api/Motor/ApprovePolicy",
            headers=headers,
            json=payload
        )
        return response

    def normalize(self, response_data: Dict) -> Dict:
        """Normalize NIA response to the shared quote format."""
        plan_details = response_data.get('PlanDetails', []) if isinstance(response_data, dict) else []
        first_plan = plan_details[0] if plan_details else {}
        covers = first_plan.get('Covers', []) if isinstance(first_plan, dict) else []
        benefits = [cover.get('Description', '') for cover in covers if cover.get('Description')]
        premium = sum(float(cover.get('CoverPremFc', 0) or 0) for cover in covers)
        coverage = float(response_data.get('VehFcValue', 0) or 0)

        return {
            'provider': self.provider_name,
            'prod_code': first_plan.get('Code'),
            'plan_name': first_plan.get('Name'),
            'premium': premium,
            'coverage': coverage,
            'benefits': benefits,
            'mandatory_covers': [c for c in covers if c.get('CoverFlag') in ['BC', 'IB', 'MC']],
            'optional_covers': [c for c in covers if c.get('CoverFlag') not in ['BC', 'IB', 'MC']],
            'reference_no': response_data.get('ReferenceNo') or response_data.get('PolRefNo'),
        }

    def _build_create_quote_payload(self, data: Dict) -> Dict:
        """Build request payload according to NIA motor quote API requirements."""
        return {
            "PolRefNo": data.get('polRefNo', ''),
            "PolPartyCode": data.get('PolPartyCode', '201001'),
            "PolDeptCode": data.get('PolDeptCode', '10'),
            "PolDivnCode": data.get('PolDivnCode', '813'),
            "PolAssrCode": data.get('PolAssrCode', '201001'),
            "PolDivnCode": data.get('PolDivnCode', '813'),
            "PolAssrType": data.get('PolAssrType', '100'),
            "PolAssrName": data.get('PolAssrName', data.get('name', 'Test')),
            "PolAssrLastName": data.get('PolAssrLastName', data.get('last_name', 'User')),
            "PolAssrDob": data.get('PolAssrDob', data.get('dob', '12/10/1988')),
            "PolAssrAge": str(data.get('age', 30)),
            "PolAssrCivilId": data.get('PolAssrCivilId', data.get('nid', '784-1990-1234567-1')),
            "PolAssrEmail": data.get('PolAssrEmail', data.get('email', 'test@example.com')),
            "PolAssrMobile": data.get('PolAssrMobile', '0551234567'),
            "PolAssrPhone": data.get('PolAssrPhone', ''),
            "PolProdCode": data.get('PolProdCode', '1002'),
            "PolSchemeType": data.get('PolSchemeType', '2'),
            "PolSiCurrCode": data.get('PolSiCurrCode', '101'),
            "PolPremCurrCode": data.get('PolPremCurrCode', '101'),
            "PolSchCode": data.get('PolSchCode', '1000'),
            "PolPrevInsValidYn": data.get('PolPrevInsValidYn', 'Y'),
            "VehChassisNo": data.get('VehChassisNo', 'RKLBB0BE4P0048836'),
            "VehUsage": data.get('VehUsage', '1001'),
            "VehMake": data.get('VehMake', '009'),
            "VehModel": data.get('VehModel', '9195'),
            "VehBodyType": data.get('VehBodyType', '001'),
            "VehNoCylinder": data.get('VehNoCylinder', '05'),
            "VehNoSeats": data.get('VehNoSeats', '5.0'),
            "VehNoDoors": data.get('VehNoDoors', '4'),
            "VehMfgYear": data.get('VehMfgYear', '2023'),
            "VehBrandNewYn": data.get('VehBrandNewYn', 'Y'),
            "VehFcValue": data.get('VehFcValue', data.get('sum_insured', 500000)),
            "VehRegion": data.get('VehRegion', 'GCC'),
            "VehRegnDt": data.get('VehRegnDt', '10/05/2021'),
            "VehAge": str(data.get('VehAge', '1.0')),
            "VehAgencyType": data.get('VehAgencyType', 'N'),
            "VehPrevInsType": data.get('VehPrevInsType', '1'),
            "VehAccident": data.get('VehAccident', 'N'),
            "VehRegnCardExp": data.get('VehRegnCardExp', 'N'),
            "PolPrevExpDt": data.get('PolPrevExpDt', '05/09/2017'),
            "VehOdometer": data.get('VehOdometer', '1')
        }

    def _auth_headers(self) -> Dict:
        if not self.token:
            self.authenticate()
        return {
            "Authorization": f"Bearer {self.token}" if self.token else "",
            "Content-Type": "application/json"
        }
