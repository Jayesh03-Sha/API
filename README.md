# Promise Insure API Test Application

## Overview

`Promise Insure API Test Application` is a Django-based insurance quotation aggregator and comparison engine for UAE-based insurance providers.

The system supports:
- JWT-based authentication
- Quote request persistence
- Parallel quote fetching from two providers: DIC and QIC
- Intelligent ranking and comparison of provider responses
- Complete test coverage for quote aggregation, scoring, and API behavior

## Features

- Two-provider comparison engine: **DIC Insurance Broker UAE** and **QIC Insurance UAE**
- Parallel provider request execution
- Smart scoring using premium, benefits, coverage, claims, and network factors
- User isolation and audit-safe quote history
- Ready to run in development with SQLite

## Quick Start

```bash
cd e:\PROMISE_INSURE_API_TEST_APPLICATION\api_test_server
python manage.py migrate
python manage.py runserver
```

Server URL: `http://localhost:8000`

## Authentication

Register and log in to acquire JWT tokens.

### Endpoints

- `POST /api/auth/register/` – Register a new user
- `POST /api/auth/login/` – Obtain JWT access token
- `GET /api/auth/profile/` – Retrieve authenticated user profile
- `POST /api/auth/logout/` – Logout

## Quote APIs

### Main quote endpoint

- `POST /api/quotes/get-quotes/`
  - Requires `Authorization: Bearer <token>`
  - Fetches quotes from configured providers and returns ranked results

### History endpoints

- `GET /api/quotes/history/` – User quote history
- `GET /api/quotes/{id}/` – Quote details by ID

## Testing

Run the test suite from the `api_test_server` folder:

```bash
python manage.py test api_set1.test_quotation -v 2
```

---

## Project Structure

- `api_test_server/` — Django project and app code
- `api_test_server/api_set1/` — Core quote models, serializers, views, tests, and provider services
- `api_test_server/ui/` — Frontend templates and admin/dashboard views
- `API_JSON_FILES/` — Sample provider request payloads
- `API_MOCK_DATA/` — Mock JSON/XML provider response files
- `Insurance_Quotation_API.postman_collection.json` — Postman collection for API testing

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | ⚡ Fast commands & examples (5-min read) |
| **[QUOTATION_API_DOCS.md](QUOTATION_API_DOCS.md)** | 📚 Complete API documentation |
| **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** | 🔧 Setup, deployment, integration |
| **[SYSTEM_SUMMARY.md](SYSTEM_SUMMARY.md)** | 📊 Project overview & architecture |
| **[Insurance_Quotation_API.postman_collection.json](Insurance_Quotation_API.postman_collection.json)** | 📬 Postman API collection |

---

## 🔐 Authentication

All quote endpoints require JWT authentication:

```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","email":"user@example.com","password":"Pass123!"}'

# 2. Login (get token)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"Pass123!"}'

# 3. Use token in requests
curl -X POST http://localhost:8000/api/quotes/get-quotes/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"insurance_type":"health","age":30,"sum_insured":500000,"city":"Dubai","members":2}'
```

---

## 📍 API Endpoints

### Authentication
```
POST   /api/auth/register/          Register new user
POST   /api/auth/login/             Login & get JWT token
GET    /api/auth/profile/           Get user profile
POST   /api/auth/logout/            Logout
```

### Quotations (require authentication)
```
POST   /api/quotes/get-quotes/      Get quotes from all providers ⭐
GET    /api/quotes/history/         Get user's quote history
GET    /api/quotes/{id}/            Get specific quote details
```

**⭐ Main endpoint:** `POST /api/quotes/get-quotes/`

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test api_set1.test_quotation -v 2

# Run specific test class
python manage.py test api_set1.test_quotation.QuoteAPITestCase -v 2

# Test providers
python manage.py test api_set1.test_quotation.DICProviderTestCase
python manage.py test api_set1.test_quotation.QICProviderTestCase

# Test aggregation
python manage.py test api_set1.test_quotation.QuoteAggregatorTestCase

# Test comparison
python manage.py test api_set1.test_quotation.QuoteComparatorTestCase

# Test APIs
python manage.py test api_set1.test_quotation.QuoteAPITestCase
```

**Test Coverage:**
- ✅ 3 Provider services
- ✅ Quote aggregation (sequential & parallel)
- ✅ Quote comparison & scoring
- ✅ 3 API endpoints + error cases
- ✅ Authentication & permissions
- ✅ Database models

---

## 🏗️ Architecture

### Project layout
```
api_test_server/
├── manage.py
├── api_test_server/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── api_set1/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                    # QuoteRequest, Quote models
│   ├── serializers.py               # Input/output validation
│   ├── urls.py                      # API routes
│   ├── views.py                     # API and provider views
│   ├── tests.py                     # Django app tests
│   ├── test_quotation.py            # comprehensive test coverage
│   ├── services/
│   │   ├── aggregator.py            # Parallel quote fetching
│   │   ├── comparator.py            # Smart comparison & scoring
│   │   └── providers/
│   │       ├── base.py              # Abstract provider base
│   │       ├── DIC.py               # DIC provider
│   │       ├── QIC.py               # QIC provider
│   │       └── NIA.py               # NIA provider
└── ui/
    ├── templates/                  # Home and dashboard UI
```

### Technology Stack
- **Framework:** Django 6.0+
- **API:** Django REST Framework
- **Auth:** JWT (djangorestframework-simplejwt)
- **Testing:** Django TestCase + APITestCase
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Caching:** Ready for Redis/Memcached

---

## 🧮 Scoring Algorithm

The system intelligently scores quotes (0-100) using:

```
api_test_server/
├── manage.py
├── api_test_server/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── api_set1/
    ├── models.py
    ├── serializers.py
    ├── urls.py
    ├── views.py
    ├── test_quotation.py
    └── services/
        ├── aggregator.py
        ├── comparator.py
        └── providers/
            ├── base.py
            ├── DIC.py
            └── QIC.py
```

## Postman

Import `Insurance_Quotation_API.postman_collection.json` to test the API endpoints.

## Recommended Documents

- `QUICK_REFERENCE.md` – Quick commands and examples
- `QUOTATION_API_DOCS.md` – Detailed API documentation
- `IMPLEMENTATION_GUIDE.md` – Setup and deployment guidance
- `SYSTEM_SUMMARY.md` – System architecture and overview

## Notes

The active Django app is located at `api_test_server/api_set1`. Existing provider integrations are implemented under `api_set1/services/providers/`.
