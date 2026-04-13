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

## Project Structure

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
