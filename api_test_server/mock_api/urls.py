from django.urls import path
from .views import MockInsuranceQuoteView

urlpatterns = [
    path('<str:provider_code>/quotes/', MockInsuranceQuoteView.as_view(), name='mock-provider-quotes'),
    
    # New Standardized API Endpoints for Realtime Simulation
    path('api/v1/User/Auth', MockInsuranceQuoteView.as_view(), {'action': 'auth'}, name='mock-auth'),
    path('api/v1/Insurance/GenerateQuote', MockInsuranceQuoteView.as_view(), {'action': 'quote'}, name='mock-generate-quote'),
    path('api/v1/Insurance/ChooseScheme', MockInsuranceQuoteView.as_view(), {'action': 'choose'}, name='mock-choose-scheme'),
    path('api/v1/Insurance/GetPaymentInfo', MockInsuranceQuoteView.as_view(), {'action': 'policy'}, name='mock-get-policy'),
    # Standardized API endpoints for mock providers
]
