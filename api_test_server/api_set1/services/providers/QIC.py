from typing import Optional, Dict, List
from .base import BaseProvider


class QICProvider(BaseProvider):
    """QIC Motor Insurance Provider using Anoud aggregator APIs."""

    def __init__(self, api_key: str = None, base_url: str = None):
        super().__init__(
            api_key=api_key or 'Basic dXNlcjpwYXNzd29yZA==',
            base_url=base_url or 'http://localhost:8000/mock-api/'
        )
        self.provider_name = 'QIC Insurance UAE'
        self.company_code = '002'

    def get_quote(self, data: Dict) -> Optional[Dict]:
        """Create a motor tariff quote using the Anoud tariff endpoint."""
        try:
            payload = self._build_tariff_payload(data)
            response, response_time = self._make_request(
                method='POST',
                endpoint='qicservices/aggregator/motor/tariff',
                headers=self._auth_headers(),
                json=payload
            )

            if not response or str(response.get('respCode', '')).strip() not in ['0', '00', '0000']:
                return None

            normalized_quote = self.normalize(response)
            normalized_quote['provider_id'] = 'qic_uae'
            normalized_quote['response_time_ms'] = response_time
            return normalized_quote
        except Exception as e:
            raise Exception(f'QIC UAE Provider Error: {str(e)}')

    def normalize(self, response_data: Dict) -> Dict:
        schemes = response_data.get('schemes') or []
        if not schemes:
            return {
                'provider': self.provider_name,
                'prod_code': None,
                'plan_name': None,
                'premium': 0.0,
                'coverage': float(response_data.get('sumInsured', 0) or 0),
                'benefits': [],
                'mandatory_covers': [],
                'optional_covers': [],
                'reference_no': response_data.get('quoteNo')
            }

        best_scheme = schemes[0]
        basic_covers = best_scheme.get('basicCovers') or []
        inclusive_covers = best_scheme.get('inclusiveCovers') or []
        optional_covers = best_scheme.get('optionalCovers') or []
        excess_covers = best_scheme.get('excessCovers') or []
        discount_covers = best_scheme.get('discountCovers') or []

        benefits = [c.get('name') for c in (basic_covers + inclusive_covers + optional_covers + excess_covers + discount_covers) if c.get('name')]

        return {
            'provider': self.provider_name,
            'prod_code': best_scheme.get('productCode'),
            'plan_name': best_scheme.get('schemeName'),
            'premium': float(best_scheme.get('netPremium', 0) or 0),
            'coverage': float(response_data.get('sumInsured', 0) or 0),
            'benefits': benefits,
            'mandatory_covers': basic_covers + inclusive_covers,
            'optional_covers': optional_covers,
            'reference_no': response_data.get('quoteNo')
        }

    def _auth_headers(self) -> Dict:
        headers = {
            'Content-Type': 'application/json',
            'company': self.company_code,
        }
        if self.api_key:
            headers['Authorization'] = self.api_key if self.api_key.startswith('Basic ') else f'Basic {self.api_key}'
        return headers

    def get_net_premium(self, quote_no: str, prod_code: str, scheme_code: str, optional_covers: List[str] = None) -> Optional[Dict]:
        payload = {
            'quoteNo': quote_no,
            'prodCode': prod_code,
            'schemeCode': scheme_code,
            'optionalCovers': optional_covers or []
        }
        response, _ = self._make_request(
            method='POST',
            endpoint='qicservices/aggregator/motor/netPremium',
            headers=self._auth_headers(),
            json=payload
        )
        return response

    def send_pay_link(self, quote_no: str, user_id: str, email_id: str, user_type: str) -> Optional[Dict]:
        payload = {
            'quoteNo': quote_no,
            'userId': user_id,
            'emailId': email_id,
            'userType': user_type,
        }
        response, _ = self._make_request(
            method='POST',
            endpoint='qicservices/aggregator/sendPayLink',
            headers=self._auth_headers(),
            json=payload
        )
        return response

    def download_quote_document(self, quote_no: str, doc_type: str) -> Optional[Dict]:
        response, _ = self._make_request(
            method='GET',
            endpoint=f'qicservices/aggregator/getQuoteSchedule?quoteNo={quote_no}&docType={doc_type}',
            headers=self._auth_headers()
        )
        return response

    def download_policy_report(self, policy_no: str, doc_type: str) -> Optional[Dict]:
        response, _ = self._make_request(
            method='GET',
            endpoint=f'qicservices/aggregator/getPolicyReport?policyNo={policy_no}&docType={doc_type}',
            headers=self._auth_headers()
        )
        return response

    def get_policy_details(self, query: Dict) -> Optional[Dict]:
        response, _ = self._make_request(
            method='POST',
            endpoint='qicservices/aggregator/getLeadPolList',
            headers=self._auth_headers(),
            json=query
        )
        return response

    def _build_tariff_payload(self, data: Dict) -> Dict:
        extras = data.get('additional_details', {}) or {}
        return {
            'insuredName': extras.get('insuredName') or data.get('insured_name', 'Test User'),
            'makeCode': extras.get('makeCode') or data.get('makeCode') or data.get('make', '001'),
            'modelCode': extras.get('modelCode') or data.get('modelCode') or data.get('model', '001'),
            'modelYear': int(extras.get('modelYear') or data.get('modelYear') or data.get('year', 2024)),
            'sumInsured': float(extras.get('sumInsured') or data.get('sumInsured') or data.get('sum_insured') or data.get('VehFcValue', 500000)),
            'vehicleType': extras.get('vehicleType') or data.get('vehicleType') or data.get('vehicle_type', '1001'),
            'vehicleUsage': extras.get('vehicleUsage') or data.get('vehicleUsage') or data.get('vehicle_usage', '1001'),
            'noOfCylinder': extras.get('noOfCylinder') or data.get('noOfCylinder') or data.get('no_of_cylinder', '05'),
            'seatingCapacity': extras.get('seatingCapacity') or data.get('seatingCapacity') or data.get('seating_capacity', '4'),
            'regYear': extras.get('regYear') or data.get('regYear') or data.get('reg_year', data.get('year', 2024)),
            'gccSpec': extras.get('gccSpec') or data.get('gccSpec') or data.get('gcc_spec', '1'),
            'previousInsuranceValid': extras.get('previousInsuranceValid') or data.get('previousInsuranceValid') or data.get('previous_insurance_valid', '1'),
            'totalLoss': extras.get('totalLoss') or data.get('totalLoss') or data.get('total_loss', '0'),
            'driverDOB': extras.get('driverDOB') or data.get('driverDOB') or data.get('driver_dob') or data.get('dob', '01/01/1990'),
            'insuredAge': int(extras.get('insuredAge') or data.get('insuredAge') or data.get('insured_age') or data.get('age', 30)),
            'noClaimYear': extras.get('noClaimYear') or data.get('noClaimYear') or data.get('no_claim_year', '0'),
            'chassisNo': extras.get('chassisNo') or data.get('chassisNo') or data.get('chassis_no') or data.get('VehChassisNo', 'JTJHY00W0J4282051'),
            'driverExp': int(extras.get('driverExp') or data.get('driverExp') or data.get('driver_experience', 1)),
            'policyFromDate': extras.get('policyFromDate') or data.get('policyFromDate') or data.get('policy_from_date', '01/01/2025'),
            'civilId': extras.get('civilId') or data.get('civilId') or data.get('civil_id') or data.get('nationalId') or data.get('national_id') or data.get('nid', '35363735322'),
            'firstRegDate': extras.get('firstRegDate') or data.get('firstRegDate') or data.get('first_reg_date', '01/01/2020'),
            'mobileNo': extras.get('mobileNo') or data.get('mobileNo') or data.get('mobile_number') or data.get('mobile', '971501234567'),
            'emailId': extras.get('emailId') or data.get('emailId') or data.get('email', 'test@example.com'),
            'poBox': extras.get('poBox') or data.get('poBox') or data.get('po_box', ''),
            'city': extras.get('city') or data.get('city') or data.get('city_code', '001'),
            'engineNo': extras.get('engineNo') or data.get('engineNo') or data.get('engine_no', 'ENG123456789'),
            'registrationNo': extras.get('registrationNo') or data.get('registrationNo') or data.get('registration_no', 'ABC123'),
            'tcfNo': extras.get('tcfNo') or data.get('tcfNo') or data.get('tcf_no', 'TCF123'),
            'colorCode': extras.get('colorCode') or data.get('colorCode') or data.get('color_code', '001'),
            'financedStatus': int(extras.get('financedStatus') or data.get('financedStatus') or data.get('financed_status', 0)),
            'plateCharacter': extras.get('plateCharacter') or data.get('plateCharacter') or data.get('plate_character', 'A'),
            'financeBank': extras.get('financeBank') or data.get('financeBank') or data.get('finance_bank', ''),
            'geoArea': extras.get('geoArea') or data.get('geoArea') or data.get('geo_area', '1001'),
            'regnLocation': extras.get('regnLocation') or data.get('regnLocation') or data.get('regn_location', '001'),
            'nationality': extras.get('nationality') or data.get('nationality') or data.get('nationality_code', '101'),
            'admeId': int(extras.get('admeId') or data.get('admeId') or data.get('adme_id', 1)),
            'leadId': int(extras.get('leadId') or data.get('leadId') or data.get('lead_id', 0)),
            'promoCode': extras.get('promoCode') or data.get('promoCode') or data.get('promo_code', ''),
        }
