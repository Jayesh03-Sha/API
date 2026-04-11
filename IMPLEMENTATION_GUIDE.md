# 🚀 Insurance Quotation Comparison System - Implementation Guide

## Overview

This guide provides step-by-step instructions to set up and deploy the multi-provider insurance quotation comparison system.

---

## 📁 Project Structure

```
api_test_server/
├── api_set1/
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── aggregator.py          # Quote aggregator (parallel calls)
│   │   ├── comparator.py           # Quote comparison & scoring
│   │   └── providers/
│   │       ├── __init__.py
│   │       ├── base.py             # Abstract base provider
│   │       ├── hdfc.py             # HDFC Ergo integration
│   │       ├── icici.py            # ICICI Lombard integration
│   │       └── star.py             # Star Health integration
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                   # QuoteRequest, Quote models
│   ├── serializers.py              # DRF serializers
│   ├── tests.py                    # Unit tests
│   ├── test_quotation.py           # Comprehensive test suite
│   ├── urls.py                     # API endpoints
│   └── views.py                    # API views
├── api_test_server/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
└── db.sqlite3
```

---

## 🔧 Installation & Setup

### 1. Install Dependencies

```bash
# Navigate to project directory
cd e:\PROMISE_INSURE_API_TEST_APPLICATION

# Create and activate virtual environment (if not already done)
python -m venv env
env\Scripts\activate

# Install required packages
pip install django djangorestframework djangorestframework-simplejwt requests
```

### 2. Run Database Migrations

```bash
cd api_test_server

# Create migration files for new models
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 3. Create Superuser (Optional, for Django Admin)

```bash
python manage.py createsuperuser
```

### 4. Run Tests

```bash
# Run all tests
python manage.py test api_set1.test_quotation

# Run with verbose output
python manage.py test api_set1.test_quotation -v 2

# Run specific test class
python manage.py test api_set1.test_quotation.QuoteAPITestCase -v 2

# Run specific test method
python manage.py test api_set1.test_quotation.QuoteAPITestCase.test_get_quotes_valid_request -v 2
```

### 5. Start Development Server

```bash
python manage.py runserver
```

Server will be available at: `http://localhost:8000`

---

## 📚 API Quick Start

### Step 1: Register User

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "testuser@example.com",
    "password": "SecurePassword123!",
    "password2": "SecurePassword123!"
  }'
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "testuser@example.com"
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Step 2: Login and Get Token

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePassword123!"
  }'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...}
}
```

**Save the `access` token for subsequent API calls.**

### Step 3: Get Insurance Quotes

```bash
curl -X POST http://localhost:8000/api/quotes/get-quotes/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "insurance_type": "health",
    "age": 30,
    "sum_insured": 500000,
    "city": "Dubai",
    "members": 2
  }'
```

**Response:**
```json
{
  "best_quote": {
    "id": 1,
    "provider": "HDFC Ergo",
    "premium": 8500.00,
    "coverage": 500000.00,
    "benefits": ["Cashless Hospitals", "No Claim Bonus"],
    "comparison_score": 92.45,
    "is_best": true,
    "response_time_ms": 245,
    "created_at": "2024-01-15T10:30:45Z"
  },
  "quotes": [
    {
      "id": 1,
      "provider": "HDFC Ergo",
      "premium": 8500.00,
      "coverage": 500000.00,
      "comparison_score": 92.45,
      "is_best": true
    },
    {
      "id": 2,
      "provider": "ICICI Lombard",
      "premium": 9100.00,
      "coverage": 500000.00,
      "comparison_score": 88.20,
      "is_best": false
    },
    {
      "id": 3,
      "provider": "Star Health",
      "premium": 8700.00,
      "coverage": 500000.00,
      "comparison_score": 90.15,
      "is_best": false
    }
  ],
  "comparison_summary": {
    "count": 3,
    "avg_premium": 8766.67,
    "min_premium": 8500.00,
    "max_premium": 9100.00,
    "premium_range": 600.00,
    "avg_score": 90.27,
    "highest_score": 92.45,
    "savings_potential": 600.00
  },
  "message": "Found 3 quotes from 3 providers"
}
```

### Step 4: Get Quote History

```bash
curl -X GET http://localhost:8000/api/quotes/history/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Step 5: Get Quote Details

```bash
curl -X GET http://localhost:8000/api/quotes/1/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## 🔌 Provider Integration

### Current Implementation

The system uses **mock providers** for testing. Each provider simulates API responses with realistic variations.

### Switching to Real APIs

To integrate with actual insurance provider APIs:

#### 1. Update Provider Service

**File:** `services/providers/hdfc.py`

```python
def get_quote(self, data: Dict) -> Optional[Dict]:
    try:
        # Replace mock with actual API call
        payload = {
            "age": data["age"],
            "sum_insured": float(data["sum_insured"]),
            "city": data["city"],
            "members": data.get("members", 1)
        }
        
        response, response_time = self._make_request(
            url=self.base_url,
            method='POST',
            json=payload
        )
        
        if response:
            normalized = self.normalize(response)
            normalized['response_time_ms'] = response_time
            return normalized
        
        return None
        
    except Exception as e:
        raise Exception(f"HDFC Provider Error: {str(e)}")
```

#### 2. Environment Configuration

**File:** `.env`

```env
HDFC_API_KEY=your_hdfc_api_key
HDFC_API_URL=https://api.your-hdfc-endpoint.com/v1/quotes

ICICI_API_KEY=your_icici_api_key
ICICI_API_URL=https://api.your-icici-endpoint.com/v1/quotes

STAR_API_KEY=your_star_api_key
STAR_API_URL=https://api.your-star-endpoint.com/v1/quotes
```

#### 3. Load Environment Variables

**File:** `settings.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

HDFC_API_KEY = os.getenv('HDFC_API_KEY')
HDFC_API_URL = os.getenv('HDFC_API_URL')

ICICI_API_KEY = os.getenv('ICICI_API_KEY')
ICICI_API_URL = os.getenv('ICICI_API_URL')

STAR_API_KEY = os.getenv('STAR_API_KEY')
STAR_API_URL = os.getenv('STAR_API_URL')
```

---

## 🎯 Key Components

### 1. Models (`models.py`)

#### QuoteRequest Model
```python
class QuoteRequest(models.Model):
    user = models.ForeignKey(User, ...)
    insurance_type = models.CharField(max_length=50)
    age = models.IntegerField()
    sum_insured = models.DecimalField(max_digits=12)
    city = models.CharField(max_length=100)
    members = models.IntegerField(default=1)
    additional_details = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Quote Model
```python
class Quote(models.Model):
    quote_request = models.ForeignKey(QuoteRequest, ...)
    provider = models.CharField(max_length=50)
    premium = models.DecimalField(max_digits=12)
    coverage = models.DecimalField(max_digits=12)
    benefits = models.JSONField(default=list)
    comparison_score = models.FloatField(default=0)
    is_best = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 2. Services

#### Provider Base Class (`services/providers/base.py`)
```python
class BaseProvider(ABC):
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
    
    @abstractmethod
    def get_quote(self, data):
        pass  # Implement in subclass
    
    @abstractmethod
    def normalize(self, response):
        pass  # Transform API response to standard format
```

#### Quote Aggregator (`services/aggregator.py`)
```python
class QuoteAggregator:
    def __init__(self, providers):
        self.providers = providers
    
    def get_all_quotes(self, data, parallel=True):
        # Fetch quotes from all providers
        # parallel=True uses ThreadPoolExecutor
        pass
```

#### Quote Comparator (`services/comparator.py`)
```python
class QuoteComparator:
    def compare_quotes(self, quotes):
        # Calculate scores and return ranked list
        pass
    
    def _calculate_score(self, quote):
        # Score = 40% Premium + 30% Benefits + ...
        pass
```

### 3. Views (`views.py`)

#### GetQuotesView
```python
class GetQuotesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # 1. Validate input
        # 2. Aggregate quotes from all providers
        # 3. Compare and score quotes
        # 4. Save to database
        # 5. Return ranked results
        pass
```

---

## 📊 Example Workflow

### Request Flow Diagram

```
User Request
    ↓
Authentication (JWT)
    ↓
Input Validation
    ↓
Create QuoteRequest (DB)
    ↓
Quote Aggregator
    ├─→ HDFC Provider
    ├─→ ICICI Provider
    └─→ Star Provider (Parallel)
    ↓
Quote Comparator
    ├─→ Calculate Scores
    ├─→ Sort by Quality
    └─→ Select Best
    ↓
Save Quotes (DB)
    ↓
Return Response
```

---

## 🧪 Testing Examples

### Test Provider Services

```bash
python manage.py test api_set1.test_quotation.HDFCProviderTestCase -v 2
```

### Test Quote Aggregation

```bash
python manage.py test api_set1.test_quotation.QuoteAggregatorTestCase.test_parallel_aggregation -v 2
```

### Test API Endpoints

```bash
python manage.py test api_set1.test_quotation.QuoteAPITestCase.test_get_quotes_valid_request -v 2
```

### Test Comparison Logic

```bash
python manage.py test api_set1.test_quotation.QuoteComparatorTestCase -v 2
```

---

## 🔐 Security Best Practices

### 1. JWT Token Management

```python
# In views.py
from rest_framework_simplejwt.authentication import JWTAuthentication

class GetQuotesView(APIView):
    permission_classes = [IsAuthenticated]  # Requires JWT token
    authentication_classes = [JWTAuthentication]
```

### 2. Input Validation

```python
# In serializers.py
class QuoteRequestSerializer(serializers.ModelSerializer):
    def validate_age(self, value):
        if value < 18 or value > 100:
            raise serializers.ValidationError("Invalid age")
        return value
```

### 3. User Isolation

```python
# In views.py - Users can only access their own quotes
quote_request = QuoteRequest.objects.get(
    id=quote_request_id,
    user=request.user  # Ensure ownership
)
```

### 4. API Key Security

```python
# In settings.py - Store in environment variables
HDFC_API_KEY = os.getenv('HDFC_API_KEY')  # Never hardcode
```

---

## 🚀 Production Deployment

### 1. Environment Configuration

Create `.env` file:
```env
DEBUG=False
SECRET_KEY=your_long_secret_key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Provider API Keys
HDFC_API_KEY=xxx
ICICI_API_KEY=xxx
STAR_API_KEY=xxx

# JWT Settings
JWT_SIGNING_KEY=your_signing_key
```

### 2. Database (PostgreSQL Recommended)

```bash
pip install psycopg2-binary
```

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', 5432),
    }
}
```

### 3. Caching (Redis Recommended)

```bash
pip install redis django-redis
```

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### 4. Rate Limiting

```bash
pip install djangorestframework-ratelimit
```

```python
# views.py
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

class GetQuotesView(APIView):
    throttle_classes = [UserRateThrottle]  # 1000/day per user
```

### 5. Logging

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/quotation_api.log',
        },
    },
    'loggers': {
        'api_set1.services': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

## 📈 Performance Optimization

### 1. Database Indexing

```python
# models.py
class Quote(models.Model):
    provider = models.CharField(max_length=50, db_index=True)
    comparison_score = models.FloatField(db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['quote_request', '-comparison_score']),
        ]
```

### 2. Query Optimization

```python
# views.py - Use select_related/prefetch_related
quote_requests = QuoteRequest.objects.filter(user=request.user).prefetch_related('quotes')
```

### 3. Caching Quotes

```python
# services/aggregator.py
from django.core.cache import cache

def get_all_quotes(self, data):
    cache_key = f"quotes:{data['age']}:{data['sum_insured']}"
    quotes = cache.get(cache_key)
    
    if not quotes:
        quotes = self._fetch_quotes(data)
        cache.set(cache_key, quotes, 3600)  # 1 hour
    
    return quotes
```

---

## 🐛 Troubleshooting

### Issue: "No module named 'services'"

**Solution:** Ensure `__init__.py` files exist in all directories:
```
services/
├── __init__.py      # Must exist
└── providers/
    ├── __init__.py  # Must exist
```

### Issue: "Database not migrated"

**Solution:** Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Issue: "Permission denied" on quote access

**Solution:** Ensure user ownership check:
```python
quote_request = QuoteRequest.objects.get(
    id=quote_request_id,
    user=request.user  # This prevents unauthorized access
)
```

### Issue: slow API responses

**Solution:** Enable parallel requests:
```python
# In views.py
quotes = aggregator.get_all_quotes(data, parallel=True)  # Default
```

---

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [JWT Authentication](https://django-rest-framework-simplejwt.readthedocs.io/)

---

**Last Updated:** January 2024
**Version:** 1.0.0
