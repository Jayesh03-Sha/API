import os
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status

class MockInsuranceQuoteView(APIView):
    """
    Mock API to simulate external insurance provider responses.
    Supports both JSON and XML formats based on the 'Accept' header or 'format' query param.
    Now supports the DIN/DIC multi-step flow.
    """
    permission_classes = [AllowAny]

    def post(self, request, provider_code=None, action=None):
        requested_format = request.query_params.get('format', 'json').lower()
        
        # DIN / DIC Flow
        if action == 'auth':
            return self._handle_auth(request)
        elif action == 'quote':
            return self._handle_generate_quote(request)
        elif action == 'choose':
            return self._handle_choose_scheme(request)
        elif action == 'policy':
            return self._handle_get_policy(request)
        elif action in ['motor/tariff', 'motor/netPremium', 'sendPayLink', 'getLeadPolList']:
            return self._handle_qic_request(request, action)

        # Fallback to existing logic for provider quote requests
        if provider_code:
            return self._handle_legacy_quote(request, provider_code, requested_format)
        
        return JsonResponse({"error": "Action or Provider Code required"}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, provider_code=None, action=None):
        if action == 'policy':
            return self._handle_get_policy(request)
        if action in ['getQuoteSchedule', 'getPolicyReport']:
            return self._handle_qic_document(request, action)
        return JsonResponse({"error": "Unsupported method"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def _handle_auth(self, request):
        username = request.data.get('userName')
        password = request.data.get('password')
        if username == "MOTOR_USER_001" and password == "123456":
            return JsonResponse({"status": 1, "data": "MOCK_JWT_TOKEN_123456789"}, status=status.HTTP_200_OK)
        return JsonResponse({"status": 0, "error": "Invalid login"}, status=status.HTTP_401_UNAUTHORIZED)

    def _handle_generate_quote(self, request):
        file_path = os.path.join(settings.BASE_DIR.parent, 'API_MOCK_DATA', 'JSON', 'dic_motor_plans.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            realtime_plans = []
            for plan in data.get('plans', []):
                realtime_plans.append({
                    "prodCode": plan.get('prodCode', '1001'),
                    "prodName": {
                        "en": plan.get('plan_name'),
                        "ar": plan.get('plan_name')
                    },
                    "sumInsured": plan.get('sumInsured', plan.get('coverage', 0)),
                    "premium": plan.get('premium', 0),
                    "covers": {
                        "mandatory": [
                            {
                                "coverCode": "10001",
                                "coverName": {
                                    "en": "Loss or Damage for Vehicle",
                                    "ar": "Loss or Damage for Vehicle"
                                },
                                "premium": 4409.6
                            },
                            {
                                "coverCode": "15001",
                                "coverName": {
                                    "en": "Third Party Bodily Injury",
                                    "ar": "Third Party Bodily Injury"
                                },
                                "premium": 1100
                            }
                        ],
                        "optional": [
                            {
                                "coverCode": "10002",
                                "coverName": {
                                    "en": "PAB to Driver",
                                    "ar": "PAB to Driver"
                                },
                                "premium": 120
                            }
                        ]
                    }
                })

            return JsonResponse({
                "statusId": "8006",
                "status": 1,
                "statusCategory": "OK",
                "message": {
                    "en": "8006:Quotation Created Successfully",
                    "ar": "8006:تم إنشاء عرض الأسعار بنجاح"
                },
                "data": realtime_plans
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({
                "statusId": "-1",
                "status": 0,
                "statusCategory": "InternalServerError",
                "message": {
                    "en": "Unable to generate quote",
                    "ar": "Unable to generate quote"
                },
                "data": None,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _handle_choose_scheme(self, request):
        prod_code = request.data.get('prodCode')
        return JsonResponse({
            "statusId": "8106",
            "status": 1,
            "statusCategory": "OK",
            "message": {
                "en": "8106:Tariff calculated successfully.",
                "ar": "8106:تم احتساب التعريفة بنجاح."
            },
            "data": {
                "quotationNo": f"PQ/13/3/{prod_code}/2025/796261",
                "sumInsured": 244871,
                "grossPremium": 1100,
                "discount": 0,
                "netPremium": 1100,
                "vat": 55,
                "netToCustomer": 1155,
                "excess": 0,
                "scheme": f"{prod_code} - Motor Third Party Liability",
                "paymentUrl": "http://localhost:8000/mock-api/payment-gateway/?q=QUO-999",
                "covers": request.data.get('covers', {"mandatory": [], "optional": []})
            }
        }, status=status.HTTP_200_OK)

    def _handle_get_policy(self, request):
        quotation_no = request.query_params.get('quotationNo') or request.data.get('quotation_no')
        return JsonResponse({
            "statusId": "8201",
            "status": 1,
            "statusCategory": "OK",
            "message": {
                "en": "8201:The policy has been generated successfully.",
                "ar": "8201:تم إنشاء السياسة بنجاح."
            },
            "data": {
                "polNo": "P/13/1001/25/020/00001",
                "polStatus": "APPROVED",
                "paymentStatus": "S",
                "scheme": "1231 - Comprehensive Gold",
                "siCurr": "AED",
                "sumInsured": "44506",
                "premCurr": "AED",
                "grossPremium": "1955",
                "discount": "0",
                "netPremium": "1955",
                "vatPerc": "5",
                "vat": "97.75",
                "payable": "2052.75",
                "excess": "",
                "documents": "BASE64_MOCK_PDF_CONTENT"
            }
        }, status=status.HTTP_200_OK)

    def _handle_qic_request(self, request, action):
        if action == 'motor/tariff':
            return self._handle_qic_motor_tariff(request)
        if action == 'motor/netPremium':
            return self._handle_qic_net_premium(request)
        if action == 'sendPayLink':
            return self._handle_qic_send_paylink(request)
        if action == 'getLeadPolList':
            return self._handle_qic_lead_pol_list(request)
        return JsonResponse({"status": 0, "message": "Unsupported QIC action"}, status=status.HTTP_400_BAD_REQUEST)

    def _handle_qic_document(self, request, action):
        if action == 'getQuoteSchedule':
            return JsonResponse({
                "status": 1,
                "quoteNo": request.query_params.get('quoteNo'),
                "documentUrl": "http://localhost:8000/mock-api/qic-quote-schedule.pdf",
                "documentType": request.query_params.get('docType', 'pdf')
            }, status=status.HTTP_200_OK)
        if action == 'getPolicyReport':
            return JsonResponse({
                "status": 1,
                "policyNo": request.query_params.get('policyNo'),
                "reportUrl": "http://localhost:8000/mock-api/qic-policy-report.pdf",
                "documentType": request.query_params.get('docType', 'pdf')
            }, status=status.HTTP_200_OK)
        return JsonResponse({"status": 0, "message": "Unsupported QIC document action"}, status=status.HTTP_400_BAD_REQUEST)

    def _handle_qic_motor_tariff(self, request):
        quote_no = "QIC-AN-0001"
        return JsonResponse({
            "respCode": 0,
            "respMessage": "Success",
            "quoteNo": quote_no,
            "sumInsured": 500000,
            "schemes": [
                {
                    "productCode": "ANOU-1001",
                    "schemeCode": "COMPREHENSIVE",
                    "schemeName": "Anoud Comprehensive",
                    "netPremium": 2100.00,
                    "basicCovers": [
                        {"code": "BC100", "name": "Own Damage", "nameAr": "ضرر ذاتي", "premium": 1500.00},
                        {"code": "BC200", "name": "Third Party Liability", "nameAr": "مسؤولية الطرف الثالث", "premium": 400.00}
                    ],
                    "inclusiveCovers": [
                        {"code": "IC100", "name": "Fire & Theft", "nameAr": "حريق وسرقة", "premium": 100.00}
                    ],
                    "optionalCovers": [
                        {"code": "OC100", "name": "Personal Accident", "nameAr": "حوادث شخصية", "premium": 100.00}
                    ],
                    "excessCovers": [],
                    "discountCovers": [],
                    "serviceTax": 105.00
                }
            ]
        }, status=status.HTTP_200_OK)

    def _handle_qic_net_premium(self, request):
        return JsonResponse({
            "respCode": 0,
            "respMessage": "Net premium calculated successfully",
            "quoteNo": request.data.get('quoteNo'),
            "prodCode": request.data.get('prodCode'),
            "schemeCode": request.data.get('schemeCode'),
            "netPremium": 2150.00,
            "vat": 107.50,
            "totalPremium": 2257.50
        }, status=status.HTTP_200_OK)

    def _handle_qic_send_paylink(self, request):
        return JsonResponse({
            "respCode": 0,
            "respMessage": "Pay link generated successfully",
            "payLink": "http://localhost:8000/pay?q=QIC-AN-0001"
        }, status=status.HTTP_200_OK)

    def _handle_qic_lead_pol_list(self, request):
        return JsonResponse({
            "respCode": 0,
            "respMessage": "Lead policy list retrieved",
            "leadPolicies": [
                {
                    "policyNo": "AN-2025-001",
                    "status": "ACTIVE",
                    "insuredName": request.data.get('insuredName', 'Test User')
                }
            ]
        }, status=status.HTTP_200_OK)

    def _handle_legacy_quote(self, request, provider_code, requested_format):
        # Original logic preserved
        insurance_type = request.data.get('insurance_type', 'health').lower()
        provider_map = {
            'dic-broker-uae': 'dic', 'qic-uae': 'qic', 'nia': 'nia', 'nia-insurance-uae': 'nia',
            'dic': 'dic', 'qic': 'qic',
        }
        base_name = provider_map.get(provider_code.lower())
        if not base_name:
            return JsonResponse({"error": f"Provider '{provider_code}' not found"}, status=status.HTTP_404_NOT_FOUND)

        filename = f"{base_name}_{insurance_type}.{requested_format}"
        file_path = os.path.join(settings.BASE_DIR.parent, 'API_MOCK_DATA', requested_format.upper(), filename)

        if not os.path.exists(file_path):
            return JsonResponse({"error": f"Mock data file not found"}, status=status.HTTP_404_NOT_FOUND)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if requested_format == 'json':
                return JsonResponse(json.loads(content), status=status.HTTP_200_OK)
            return HttpResponse(content, content_type='application/xml', status=status.HTTP_200_OK)
