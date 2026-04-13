"""
Comprehensive tests for the Insurance Quotation Comparison System

Tests cover:
- Provider API integrations
- Quote aggregation
- Quote comparison and scoring
- API endpoints
- Authentication and permissions
"""

import json
from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from unittest.mock import patch, MagicMock
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import QuoteRequest, Quote, UserProfile, InsuranceProvider
from .services.providers.DIC import DICProvider
from .services.providers.QIC import QICProvider
from .services.providers.NIA import NIAProvider
from .services.aggregator import QuoteAggregator
from .services.comparator import QuoteComparator


# ============================================================================
# Provider Tests
# ============================================================================

class DICProviderTestCase(TestCase):
    """Test DIC Provider Service"""
    
    def setUp(self):
        self.provider = DICProvider()
        self.test_data = {
            'age': 30,
            'sum_insured': 500000,
            'city': 'Dubai',
            'members': 2,
            'nid': '784-1990-1234567-1'
        }
    
    def test_provider_initialization(self):
        """Test provider is initialized correctly"""
        self.assertEqual(self.provider.provider_name, 'DIC Insurance Broker UAE')
        self.assertIsNotNone(self.provider.api_key)
    
    # Note: get_quote calls the mock API which might not be running during tests
    # unless we mock the request or start the server. 
    # For unit tests, we at least test the normalization and initialization.

class QICProviderTestCase(TestCase):
    """Test QIC Provider Service"""
    
    def setUp(self):
        self.provider = QICProvider()
        self.test_data = {
            'age': 28,
            'sum_insured': 600000,
            'city': 'Sharjah',
            'members': 2,
            'nid': '784-1990-1234567-1'
        }
    
    def test_provider_initialization(self):
        """Test provider is initialized correctly"""
        self.assertEqual(self.provider.provider_name, 'QIC Insurance UAE')


class NIAProviderTestCase(TestCase):
    """Test NIA Provider Service"""

    def setUp(self):
        self.provider = NIAProvider()
        self.test_data = {
            'age': 30,
            'sum_insured': 500000,
            'city': 'Dubai',
            'members': 2,
            'nid': '784-1990-1234567-1',
            'polAssrName': 'Test User',
            'polAssrLastName': 'Tester',
            'VehChassisNo': 'RKLBB0BE4P0048836',
            'VehModel': '9195',
            'VehMake': '009',
            'VehMfgYear': '2023',
        }

    def test_provider_initialization(self):
        """Test provider is initialized correctly"""
        self.assertEqual(self.provider.provider_name, 'NIA Insurance UAE')


# ============================================================================
# Aggregator Tests
# ============================================================================

class QuoteAggregatorTestCase(TestCase):
    """Test Quote Aggregator Service"""
    
    def setUp(self):
        # Seed some providers for the aggregator to find
        InsuranceProvider.objects.create(
            name="DIC UAE",
            code="dic-broker-uae",
            is_active=True,
            provider_class_path="api_set1.services.providers.DIC.DICProvider"
        )
        InsuranceProvider.objects.create(
            name="QIC UAE",
            code="qic-uae",
            is_active=True,
            provider_class_path="api_set1.services.providers.QIC.QICProvider"
        )
        InsuranceProvider.objects.create(
            name="NIA UAE",
            code="nia-uae",
            is_active=True,
            provider_class_path="api_set1.services.providers.NIA.NIAProvider"
        )
        
        self.aggregator = QuoteAggregator()
        self.test_data = {
            'age': 30,
            'sum_insured': 500000,
            'city': 'Dubai',
            'members': 2,
            'insurance_type': 'health',
            'nid': '784-1990-1234567-1'
        }
    
    def test_aggregator_initialization(self):
        """Test aggregator has all providers"""
        self.assertEqual(len(self.aggregator.providers), 2)


# ============================================================================
# Comparator Tests
# ============================================================================

class QuoteComparatorTestCase(TestCase):
    """Test Quote Comparator Service"""
    
    def setUp(self):
        self.comparator = QuoteComparator()
        self.sample_quotes = [
            {
                'provider': 'DIC Insurance Broker UAE',
                'premium': 8500,
                'coverage': 500000,
                'benefits': ['Cashless Hospitals', 'No Claim Bonus'],
                'claim_settlement_ratio': 95
            },
            {
                'provider': 'QIC Insurance UAE',
                'premium': 8700,
                'coverage': 500000,
                'benefits': ['Cashless', 'Ambulance', 'Health Checkup'],
                'network_hospitals': 11000
            }
        ]
    
    def test_score_calculation(self):
        """Test score calculation for a quote"""
        quote = self.sample_quotes[0]
        score = self.comparator._calculate_score(quote)
        
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_compare_quotes(self):
        """Test comparing multiple quotes"""
        best_quote, sorted_quotes = self.comparator.compare_quotes(self.sample_quotes)
        
        self.assertIsNotNone(best_quote)
        self.assertEqual(len(sorted_quotes), 2)
        self.assertTrue(sorted_quotes[0]['is_best'])
        
        # Verify sorting by score
        scores = [q['score'] for q in sorted_quotes]
        self.assertEqual(scores, sorted(scores, reverse=True))


# ============================================================================
# API Endpoint Tests
# ============================================================================

class QuoteAPITestCase(APITestCase):
    """Test Quote API Endpoints"""
    
    def setUp(self):
        """Set up test user and client"""
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123!'
        )
        UserProfile.objects.create(user=self.user)
        
        # Get tokens
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Create client and set authentication
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Seed providers
        InsuranceProvider.objects.create(
            name="DIC UAE",
            code="dic-broker-uae",
            is_active=True,
            provider_class_path="api_set1.services.providers.DIC.DICProvider"
        )
        InsuranceProvider.objects.create(
            name="NIA UAE",
            code="nia-uae",
            is_active=True,
            provider_class_path="api_set1.services.providers.NIA.NIAProvider"
        )
        
        self.base_url = '/api'
    
    def test_user_not_authenticated_cannot_get_quotes(self):
        """Test unauthenticated user cannot get quotes"""
        client = APIClient()
        data = {
            'insurance_type': 'health',
            'age': 30,
            'sum_insured': 500000,
            'city': 'Dubai',
            'members': 2,
            'nid': '784-1990-1234567-1'
        }
        response = client.post(f'{self.base_url}/quotes/get-quotes/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_quotes_invalid_age(self):
        """Test quote request with invalid age"""
        data = {
            'insurance_type': 'health',
            'age': 15,  # Too young
            'sum_insured': 500000,
            'city': 'Dubai',
            'members': 2
        }
        response = self.client.post(f'{self.base_url}/quotes/get-quotes/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('age', response.data['errors'])

class DICMultiStepFlowTestCase(TestCase):
    """Test the complete 4-step flow for DIC Provider"""
    
    def setUp(self):
        self.provider = DICProvider(base_url='http://localhost:8000/mock-api/')
        self.test_data = {
            'request_id': 'TEST-REQ-001',
            'nid': '784-1990-1234567-1',
            'chassis_number': 'WBAXXXXXXXXXXXXXXXX',
            'make': 'NISSAN',
            'model': 'PATHFINDER',
            'year': 2024
        }

    @patch('requests.post')
    @patch('requests.get')
    def test_complete_flow(self, mock_get, mock_post):
        """Test Auth -> Quote -> Choose -> Policy flow"""
        # Mock Auth Response
        mock_post.side_effect = [
            # Auth
            MagicMock(status_code=200, json=lambda: {"status": 1, "data": "MOCK_JWT_TOKEN_123456789"}),
            # Generate Quote
            MagicMock(status_code=200, json=lambda: [{
                "prodCode": "1001",
                "prodName": "Comprehensive Gold",
                "sumInsured": 244871,
                "covers": {"mandatory": ["Agency Repair"], "optional": ["Roadside"]}
            }]),
            # Choose Scheme
            MagicMock(status_code=200, json=lambda: {
                "quotationNo": "QUO-1001-999",
                "paymentUrl": "http://mock-payment"
            })
        ]
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {
            "polNo": "P123",
            "polStatus": "APPROVED",
            "paymentStatus": "S"
        })

        # 1. Auth
        token = self.provider.authenticate()
        self.assertIsNotNone(token)
        self.assertEqual(token, "MOCK_JWT_TOKEN_123456789")

        # 2. Generate Quote
        quote = self.provider.get_quote(self.test_data)
        self.assertIsNotNone(quote)
        self.assertEqual(quote['prod_code'], '1001')
        self.assertEqual(quote['plan_name'], 'Comprehensive Gold')
        self.assertGreater(len(quote['benefits']), 0)

        # 3. Choose Scheme
        scheme = self.provider.choose_scheme('1001')
        self.assertIsNotNone(scheme)
        self.assertIn('paymentUrl', scheme)
        self.assertEqual(scheme['quotationNo'], 'QUO-1001-999')

        # 4. Get Policy
        policy = self.provider.get_policy('QUO-1001-999')
