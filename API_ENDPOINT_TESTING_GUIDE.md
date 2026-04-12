# API Endpoint Testing Guide

This guide provides everything needed to test the Promise Insurance Service APIs via Postman or Curl.

## 🔑 Authentication
The system uses JWT (JSON Web Token) for all protected routes.

### 1. Register User
- **Endpoint**: `POST /api/auth/register/`
- **Body**: 
  ```json
  {
    "username": "testuser",
    "email": "test@example.com",
    "password": "Password123!",
    "password2": "Password123!"
  }
  ```

### 2. Login (Get Access Token)
- **Endpoint**: `POST /api/auth/login/`
- **Body**:
  ```json
  {
    "username": "testuser",
    "password": "Password123!"
  }
  ```
- **Response**: Keep the `access` token for the `Authorization: Bearer <token>` header.

---

## 📄 Quotation Engine
The core service that aggregates and compares quotes from multiple providers.

### 1. Fetch Aggregated Quotes
- **Endpoint**: `POST /api/quotes/get-quotes/`
- **Headers**: `Authorization: Bearer <token>`
- **Body**:
  ```json
  {
    "insurance_type": "motor",
    "age": 35,
    "sum_insured": 50000,
    "city": "Dubai",
    "members": 1,
    "additional_details": {
        "make": "NISSAN",
        "model": "PATHFINDER"
    }
  }
  ```
- **Validation**:
  - Verify `best_quote` is present.
  - Verify `scoring_breakdown` exists for each quote.
  - Verify `comparison_summary` shows accurate averages and ranges.

### 2. Get Quote History
- **Endpoint**: `GET /api/quotes/history/`
- **Headers**: `Authorization: Bearer <token>`

---

## 🛠️ Mock API (External Simulation)
Simulates external insurance providers (DIC, QIC).

### 1. Provider Quotation (JSON)
- **Endpoint**: `POST /mock-api/{provider}/quotes/`
- **Example**: `/mock-api/dic/quotes/`
- **Headers**: `Accept: application/json`

### 2. Provider Quotation (XML)
- **Endpoint**: `POST /mock-api/{provider}/quotes/?format=xml`
- **Headers**: `Accept: application/xml`

---

## 💼 CRM & Invoice Endpoints
Manage leads, deals, and transactions.

### 1. List Leads
- **Endpoint**: `GET /api/leads/` (if implemented via admin/api)

### 2. Transaction Details
- **Endpoint**: `GET /api/transactions/{id}/`
