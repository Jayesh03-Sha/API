# Promise Insurance Services: Master System Guide

This document provides a comprehensive overview of the Promise Insurance Pro Portal, its architecture, API implementation procedures, and database logic.

## 1. System Architecture

The application is built on **Django 6.0**, following a modular architecture:
- **`api_set1`**: Core engine handling API requests, insurance provider aggregation, and intelligent comparison logic.
- **`ui`**: Premium portal interface and staff-facing CRM dashboard.
- **`mock_api`**: Simulation layer for testing external insurance provider responses.

### Data Flow
1. **User Query**: Client submits insurance requirements via the Portal.
2. **Aggregation**: `QuoteAggregator` triggers parallel requests to configured providers.
3. **Comparison**: `QuoteComparator` applies weighted scoring (Premium 40%, Benefits 30%, Coverage 15%, etc.).
4. **Storage**: Quotes are persisted in the database with scoring breakdowns.
5. **Selection**: User chooses a plan, triggering a mock payment and policy generation flow.

---

## 2. API Implementation Procedure

To add a new insurance provider to the system, follow these steps:

### Step A: Create the Provider Class
Create a new file in `api_set1/services/providers/` (e.g., `AXA.py`) inheriting from `BaseProvider`.

```python
from .base import BaseProvider

class AXAProvider(BaseProvider):
    def get_quote(self, data):
        # Implement AXA specific API calls here
        # Return a standardized dictionary
        return {
            "provider": "axa",
            "premium": 1200,
            "coverage": 500000,
            "benefits": ["OPD Coverage", "Dental"],
            # ... other fields
        }
```

### Step B: Register the Provider in DB
Add the provider via the Django Admin or a seed script:
- **Name**: AXA Gulf
- **Code**: axa-gulf
- **Class Path**: `api_set1.services.providers.AXA.AXAProvider`
- **Base URL**: The AXA API endpoint.

---

## 3. Real Working API Documentation

### Get Quotes
**Endpoint**: `POST /api/quotes/get-quotes/`  
**Authentication**: Bearer Token (JWT)  
**Request Body**:
```json
{
    "insurance_type": "health",
    "age": 35,
    "city": "Dubai",
    "members": 1,
    "sum_insured": 500000
}
```

### Fetch From Database
**Endpoint**: `GET /api/quotes/{request_id}/`  
**Description**: Retrieves previously generated quotes and comparison scores for a specific request.

---

## 4. Key Database Models

### `QuoteRequest`
Stores the parameters of a user's search (age, city, etc.).

### `Quote`
Stores individual responses from providers with their `comparison_score`.

### `InsuranceProvider`
Configuration table for management to enable/disable companies and update API keys dynamically.

---

## 5. Deployment & Execution
1. **Migrations**: `python manage.py migrate`
2. **Seeding**: `python seed_providers.py`
3. **Run Server**: `python manage.py runserver`

---
*Created by Antigravity for Promise Insurance Services Ltd.*
