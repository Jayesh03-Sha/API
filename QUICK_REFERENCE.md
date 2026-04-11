# 📋 Insurance Quotation API - Quick Reference

## 🚀 Quick Start (5 minutes)

```bash
# 1. Install dependencies
pip install django djangorestframework djangorestframework-simplejwt requests

# 2. Run migrations
python manage.py migrate

# 3. Start server
python manage.py runserver

# 4. Run tests
python manage.py test api_set1.test_quotation
```

---

## 🔐 Authentication

```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Password123!",
    "password2": "Password123!"
  }'

# 2. Login (get access token)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Password123!"
  }'

# Response includes: access, refresh, user
# Save the "access" token ↓
```

---

## 📊 Get Quotes

```bash
curl -X POST http://localhost:8000/api/quotes/get-quotes/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "insurance_type": "health",
    "age": 30,
    "sum_insured": 500000,
    "city": "Dubai",
    "members": 2
  }'
```

**Request Parameters:**
| Field | Type | Valid Values |
|-------|------|--------------|
| `insurance_type` | string | health, travel, motor, home |
| `age` | int | 18-100 |
| `sum_insured` | decimal | 1-10000000 |
| `city` | string | Dubai, Abu Dhabi, etc. |
| `members` | int | 1-10 |

**Response Fields:**
```json
{
  "best_quote": { ... },      // Best option
  "quotes": [ ... ],          // All quotes (ranked)
  "comparison_summary": {     // Statistics
    "count": 3,
    "avg_premium": 8766.67,
    "premium_range": 600,
    "savings_potential": 600
  }
}
```

---

## 📜 Quote History

```bash
curl -X GET http://localhost:8000/api/quotes/history/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:** List of all user's quote requests with results

---

## 📌 Quote Details

```bash
curl -X GET http://localhost:8000/api/quotes/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:** Full details of specific quote request

---

## 🧪 Test Commands

```bash
# All tests
python manage.py test api_set1.test_quotation -v 2

# Specific test class
python manage.py test api_set1.test_quotation.QuoteAPITestCase -v 2

# Specific test method
python manage.py test api_set1.test_quotation.QuoteAPITestCase.test_get_quotes_valid_request

# With coverage
pip install coverage
coverage run --source='.' manage.py test api_set1.test_quotation
coverage report
```

---

## 🔌 API Endpoints Cheat Sheet

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/api/auth/register/` | ❌ | Create account |
| POST | `/api/auth/login/` | ❌ | Get JWT token |
| GET | `/api/auth/profile/` | ✅ | View profile |
| POST | `/api/auth/logout/` | ✅ | Logout |
| POST | `/api/quotes/get-quotes/` | ✅ | Get quotes |
| GET | `/api/quotes/history/` | ✅ | View history |
| GET | `/api/quotes/{id}/` | ✅ | View details |

---

## 💡 Code Examples

### Python - Get Quotes Directly

```python
from api_set1.services.aggregator import QuoteAggregator
from api_set1.services.comparator import QuoteComparator

# Setup
aggregator = QuoteAggregator()
comparator = QuoteComparator()

# Get quotes
data = {
    'age': 30,
    'sum_insured': 500000,
    'city': 'Dubai',
    'members': 2
}

quotes = aggregator.get_all_quotes(data, parallel=True)
best_quote, sorted_quotes = comparator.compare_quotes(quotes)

print(f"Best: {best_quote['provider']} - {best_quote['premium']}")
```

### JavaScript - Fetch Quotes

```javascript
const token = 'your_access_token';
const data = {
  insurance_type: 'health',
  age: 30,
  sum_insured: 500000,
  city: 'Dubai',
  members: 2
};

fetch('http://localhost:8000/api/quotes/get-quotes/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(data)
})
.then(r => r.json())
.then(data => {
  console.log('Best Quote:', data.best_quote);
  console.log('All Quotes:', data.quotes);
});
```

---

## ⚠️ Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `No module named 'services'` | Missing `__init__.py` | Create `services/__init__.py` |
| `Operational error: Table does not exist` | Not migrated | Run `python manage.py migrate` |
| `401 Unauthorized` | Missing/invalid token | Include `Authorization: Bearer token` header |
| `400 Bad Request` | Invalid input | Check age (18-100), sum_insured (>0), members (1-10) |

---

## 🎯 Scoring Algorithm Quick Reference

```
Score (0-100) = 
  (Premium_Score × 0.40) +
  (Benefits_Score × 0.30) +
  (Coverage_Score × 0.15) +
  (Claim_Ratio × 0.10) +
  (Network_Score × 0.05)
```

**Higher Score = Better Quote**

---

## 📁 Key Files Overview

```
api_set1/
├── models.py                    # Database models
├── views.py                     # API endpoints
├── serializers.py               # Input/output validation
├── urls.py                      # Routes
├── test_quotation.py            # 50+ tests
├── services/
│   ├── aggregator.py            # Parallel quote fetching
│   ├── comparator.py            # Quote scoring & ranking
│   └── providers/
│       ├── base.py              # BaseProvider class
│       ├── hdfc.py              # HDFC provider
│       ├── icici.py             # ICICI provider
│       └── star.py              # Star provider
```

---

## 🔒 Security Checklist

- ✅ JWT authentication on all quote endpoints
- ✅ Input validation (age, sum_insured, members)
- ✅ User isolation (can't access other users' quotes)
- ✅ API keys in environment variables
- ✅ Prepared for HTTPS in production
- ✅ Error messages don't leak sensitive info

---

## ⚡ Performance Tips

```python
# Use parallel for faster results (DEFAULT)
quotes = aggregator.get_all_quotes(data, parallel=True)  # ~300ms

# Sequential if needed (slower)
quotes = aggregator.get_all_quotes(data, parallel=False)  # ~2s

# Cache results
cache.set('quotes:key', quotes, 3600)  # 1 hour TTL
```

---

## 🧪 Testing Quick Commands

```bash
# Run all tests with verbose output
python manage.py test api_set1.test_quotation -v 2

# Test specific test class
python manage.py test api_set1.test_quotation.QuoteAPITestCase -v 2

# Test API endpoints only
python manage.py test api_set1.test_quotation.QuoteAPITestCase

# Test services only
python manage.py test api_set1.test_quotation.QuoteComparatorTestCase

# Test with coverage report
coverage run --source='.' manage.py test api_set1.test_quotation
coverage report --skip-covered
```

---

## 📊 Database Models

### QuoteRequest
```python
user          → User (ForeignKey)
insurance_type → health, travel, motor, home
age           → 18-100
sum_insured   → Decimal
city          → String
members       → 1-10
additional_details → JSON
created_at    → DateTime
```

### Quote
```python
quote_request → QuoteRequest (ForeignKey)
provider      → hdfc, icici, star
premium       → Decimal
coverage      → Decimal
benefits      → JSON (list)
comparison_score → Float (0-100)
is_best       → Boolean
response_time_ms → Integer
created_at    → DateTime
```

---

## 🚀 Deployment Checklist

- [ ] Create `.env` file with secrets
- [ ] Change `DEBUG = False` in settings
- [ ] Set `ALLOWED_HOSTS`
- [ ] Use PostgreSQL (not SQLite)
- [ ] Configure Redis for caching
- [ ] Enable HTTPS
- [ ] Set up SSL certificate
- [ ] Configure CORS if frontend is separate
- [ ] Set up logging
- [ ] Configure email for notifications
- [ ] Run `collectstatic`
- [ ] Set environment variables on server

---

## 📱 Integration with Frontend

```javascript
// React example
const [quotes, setQuotes] = useState(null);
const [loading, setLoading] = useState(false);

const getQuotes = async (formData) => {
  setLoading(true);
  const res = await fetch('/api/quotes/get-quotes/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(formData)
  });
  const data = await res.json();
  setQuotes(data);
  setLoading(false);
};
```

---

## 🆘 Quick Debug Commands

```bash
# Check if migrations are applied
python manage.py showmigrations

# Run migrations if needed
python manage.py migrate

# Create test user
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.create_user('test', 'test@test.com', 'pass')

# Check database
python manage.py dbshell

# Run specific provider test
python manage.py test api_set1.test_quotation.HDFCProviderTestCase
```

---

## 📚 Additional Help

See full documentation in:
- `QUOTATION_API_DOCS.md` - Complete API reference
- `IMPLEMENTATION_GUIDE.md` - Setup & deployment
- `SYSTEM_SUMMARY.md` - Project overview
- `test_quotation.py` - Test examples

---

**Version:** 1.0.0
**Last Updated:** January 2024
**Status:** Production Ready ✅
