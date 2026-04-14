from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
import logging
from django.http import HttpResponse

from .serializers import (
    RegisterSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    QuoteRequestSerializer,
    QuoteSerializer,
    QuoteResponseSerializer
)
from .models import QuoteRequest, Quote
from .services.aggregator import QuoteAggregator
from .services.comparator import QuoteComparator

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    """
    API endpoint for user registration.
    POST /api/auth/register/ - Register a new user
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'User registered successfully',
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    API endpoint for user login with JWT tokens.
    POST /api/auth/login/ - Login with username and password
    Returns access and refresh tokens along with user details
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class UserProfileView(APIView):
    """
    API endpoint for retrieving current user profile.
    GET /api/auth/profile/ - Get current user profile
    PUT /api/auth/profile/ - Update current user profile
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current user profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """Update current user profile"""
        user = request.user
        data = request.data
        
        # Update user fields
        if 'email' in data:
            if User.objects.filter(email=data['email']).exclude(id=user.id).exists():
                return Response(
                    {'email': 'Email already in use.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.email = data['email']
        
        if 'first_name' in data:
            user.first_name = data['first_name']
        
        if 'last_name' in data:
            user.last_name = data['last_name']
        
        user.save()

        # Update profile fields
        if hasattr(user, 'profile'):
            profile = user.profile
            if 'phone_number' in data:
                profile.phone_number = data['phone_number']
            if 'organization' in data:
                profile.organization = data['organization']
            profile.save()

        serializer = UserSerializer(user)
        return Response({
            'message': 'Profile updated successfully',
            'user': serializer.data
        }, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """
    API endpoint for changing password.
    POST /api/auth/change-password/ - Change password (requires old password)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.data['old_password']):
                return Response(
                    {'old_password': 'Wrong password.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.data['new_password'])
            user.save()
            
            return Response(
                {'message': 'Password changed successfully'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    API endpoint for user logout.
    POST /api/auth/logout/ - Logout user (invalidate refresh token)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response(
                {'message': 'Logout successful'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================================================
# Quote Management Views
# ============================================================================

class GetQuotesView(APIView):
    """
    API endpoint for getting insurance quotes from multiple providers.
    
    POST /api/quotes/get-quotes/
    
    Request body:
    {
        "insurance_type": "health",
        "age": 30,
        "sum_insured": 500000,
        "city": "Dubai",
        "members": 2,
        "additional_details": {}
    }
    
    Returns: Best quote + all quoted from all providers with comparison scores
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Get quotes from multiple insurance providers"""
        try:
            # Validate request data
            serializer = QuoteRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save quote request
            quote_request = serializer.save(user=request.user)
            
            # Prepare data for aggregator
            quote_data = {
                'age': quote_request.age,
                'sum_insured': float(quote_request.sum_insured),
                'city': quote_request.city,
                'members': quote_request.members,
                'insurance_type': quote_request.insurance_type,
                'additional_details': quote_request.additional_details or {}
            }
            
            logger.info(f"Fetching quotes for user {request.user.username} - {quote_request.insurance_type}")
            
            # Get quotes from all providers in parallel
            aggregator = QuoteAggregator()
            provider_quotes = aggregator.get_all_quotes(quote_data, parallel=True)
            
            if not provider_quotes:
                return Response(
                    {'error': 'No quotes available from providers. Please try again later.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Compare quotes and get best option
            comparator = QuoteComparator()
            best_quote, sorted_quotes = comparator.compare_quotes(provider_quotes)
            
            # Save quotes to database
            for quote_data_item in sorted_quotes:
                quote_obj = Quote.objects.create(
                    quote_request=quote_request,
                    provider=quote_data_item.get('provider', ''),
                    premium=quote_data_item.get('premium', 0),
                    coverage=quote_data_item.get('coverage', 0),
                    benefits=quote_data_item.get('benefits', []),
                    comparison_score=quote_data_item.get('score', 0),
                    scoring_breakdown=quote_data_item.get('scoring_breakdown', {}),
                    competitive_advantages=quote_data_item.get('competitive_advantages', []),
                    verdict=quote_data_item.get('verdict', ''),
                    is_best=(quote_data_item == best_quote),
                    provider_metadata={
                        'reference_no': quote_data_item.get('reference_no'),
                        'prod_code': quote_data_item.get('prod_code'),
                        'provider_id': quote_data_item.get('provider_id'),
                    }
                )
            
            # Fetch updated quotes from database
            db_quotes = Quote.objects.filter(quote_request=quote_request).order_by('-comparison_score')
            db_best_quote = db_quotes.first()
            
            # Prepare response
            response_data = {
                'best_quote': QuoteSerializer(db_best_quote).data if db_best_quote else None,
                'quotes': QuoteSerializer(db_quotes, many=True).data,
                'comparison_summary': comparator.get_comparison_summary(sorted_quotes),
                'message': f'Found {len(sorted_quotes)} quotes from {len(provider_quotes)} providers'
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in GetQuotesView: {str(e)}", exc_info=True)
            return Response(
                {'error': 'An error occurred while fetching quotes. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuoteHistoryView(APIView):
    """
    API endpoint for retrieving user's quote history.
    
    GET /api/quotes/history/ - Get all quotes requested by the user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's quote request history"""
        try:
            # Get all quote requests for the user
            quote_requests = QuoteRequest.objects.filter(user=request.user).prefetch_related('quotes')
            
            # Prepare response with quote details
            history = []
            for quote_request in quote_requests:
                quotes = quote_request.quotes.all()
                best_quote = quotes.filter(is_best=True).first()
                
                history.append({
                    'id': quote_request.id,
                    'insurance_type': quote_request.insurance_type,
                    'age': quote_request.age,
                    'sum_insured': str(quote_request.sum_insured),
                    'city': quote_request.city,
                    'members': quote_request.members,
                    'quotes_count': quotes.count(),
                    'best_quote': QuoteSerializer(best_quote).data if best_quote else None,
                    'all_quotes': QuoteSerializer(quotes.order_by('-comparison_score'), many=True).data,
                    'created_at': quote_request.created_at
                })
            
            return Response({
                'count': len(history),
                'history': history
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in QuoteHistoryView: {str(e)}", exc_info=True)
            return Response(
                {'error': 'An error occurred while retrieving quote history.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuoteDetailView(APIView):
    """
    API endpoint for retrieving a specific quote request with all details.
    
    GET /api/quotes/{quote_request_id}/ - Get specific quote request with all provider quotes
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, quote_request_id):
        """Get detailed information about a specific quote request"""
        try:
            # Get quote request, ensure it belongs to the user
            quote_request = QuoteRequest.objects.get(
                id=quote_request_id,
                user=request.user
            )
            
            # Get all quotes for this request
            quotes = Quote.objects.filter(quote_request=quote_request).order_by('-comparison_score')
            
            if not quotes.exists():
                return Response(
                    {'error': 'No quotes found for this request.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            best_quote = quotes.filter(is_best=True).first()
            
            return Response({
                'quote_request': QuoteRequestSerializer(quote_request).data,
                'best_quote': QuoteSerializer(best_quote).data if best_quote else None,
                'all_quotes': QuoteSerializer(quotes, many=True).data,
                'comparison_summary': {
                    'count': quotes.count(),
                    'avg_premium': round(sum(float(q.premium) for q in quotes) / quotes.count(), 2),
                    'min_premium': round(min(float(q.premium) for q in quotes), 2),
                    'max_premium': round(max(float(q.premium) for q in quotes), 2),
                    'premium_range': round(max(float(q.premium) for q in quotes) - min(float(q.premium) for q in quotes), 2),
                    'avg_score': round(sum(float(q.comparison_score) for q in quotes) / quotes.count(), 2),
                }
            }, status=status.HTTP_200_OK)
            
        except QuoteRequest.DoesNotExist:
            return Response(
                {'error': 'Quote request not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in QuoteDetailView: {str(e)}", exc_info=True)
            return Response(
                {'error': 'An error occurred while retrieving quote details.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def get_provider_instance(provider_name):
    import importlib
    from .models import InsuranceProvider
    provider_data = InsuranceProvider.objects.filter(name=provider_name, is_active=True).first()
    if not provider_data:
        return None
    try:
        module_path, class_name = provider_data.provider_class_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        provider_class = getattr(module, class_name)
        instance = provider_class(
            api_key=provider_data.api_key,
            base_url=provider_data.api_base_url
        )
        instance.provider_name = provider_name
        return instance
    except Exception as e:
        logger.error(f"Error loading provider {provider_name}: {str(e)}")
        return None


class SelectSchemeView(APIView):
    """
    Step 3: Select Scheme for a quote.
    POST /api/quotes/{quote_id}/select-scheme/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, quote_id):
        from django.shortcuts import get_object_or_404
        quote = get_object_or_404(Quote, id=quote_id)
        
        provider_instance = get_provider_instance(quote.provider)
        if not provider_instance:
            return Response({'error': 'Provider not available'}, status=status.HTTP_400_BAD_REQUEST)
        
        provider_id = quote.provider_metadata.get('provider_id')
        ref_no = quote.provider_metadata.get('reference_no')
        prod_code = quote.provider_metadata.get('prod_code')
        
        if provider_id == 'dic_broker_uae':
            covers = request.data.get('covers', {})
            result = provider_instance.choose_scheme(prod_code, covers)
            if result:
                return Response({
                    "message": "Scheme selected successfully",
                    "payment_url": f"https://mock-payment-gateway.com/dic-pay/{prod_code}"
                })
                
        return Response({'error': 'Failed to select scheme'}, status=status.HTTP_400_BAD_REQUEST)


class GetPolicyView(APIView):
    """
    Step 5: Process payment and get final policy.
    POST /api/quotes/{quote_id}/get-policy/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, quote_id):
        from django.shortcuts import get_object_or_404
        quote = get_object_or_404(Quote, id=quote_id)
        provider_instance = get_provider_instance(quote.provider)
        
        if not provider_instance:
            return Response({'error': 'Provider not available'}, status=status.HTTP_400_BAD_REQUEST)
            
        provider_id = quote.provider_metadata.get('provider_id')
        ref_no = quote.provider_metadata.get('reference_no')
        quotation_no = request.data.get('quotation_no', '')

        if provider_id == 'dic_broker_uae':
            policy_info = provider_instance.get_policy(quotation_no)
            if policy_info:
                return Response({
                    "message": "Policy generated successfully",
                    "policy_info": policy_info,
                    "status": "Active"
                })

        return Response({'error': 'Failed to generate policy'}, status=status.HTTP_400_BAD_REQUEST)
