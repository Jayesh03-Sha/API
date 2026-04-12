# 🚦 Postman API Testing List

This document contains all the endpoints, example payloads, and instructions for testing the **Promise Insurance Services** API and its multi-provider comparison engine.

## 🔗 Environment Setup
- **Base URL**: `http://localhost:8000`
- **Auth Strategy**: Bearer Token (JWT)

---

## 1. Authentication
*All endpoints prefixed with `/api/auth/`*

### 📥 Register
- **Endpoint**: `POST /register/`
- **Auth**: None
- **Payload**:
```json
{
  "username": "testuser",
  "email": "testuser@example.com",
  "first_name": "Test",
  "last_name": "User",
  "password": "SecurePassword123!",
  "password2": "SecurePassword123!"
}
```

### 🔐 Login
- **Endpoint**: `POST /login/`
- **Auth**: None
- **Payload**:
```json
{
  "username": "testuser",
  "password": "SecurePassword123!"
}
```
*Tip: Copy the `access` token from response for subsequent requests.*

---

## 2. Quotation Engine (Comparison)
*All endpoints prefixed with `/api/quotes/`*

### 🧪 Scenario A: Basic Health Plan (Sum Insured < 300k)
- **Endpoint**: `POST /get-quotes/`
- **Auth**: Bearer Token
- **Payload**:
```json
{
  "insurance_type": "health",
  "age": 30,
  "sum_insured": 250000,
  "city": "Dubai",
  "members": 1,
  "nid": "784-1990-1234567-1"
}
```

### 🧪 Scenario B: Standard Family Plan (Sum Insured 300k - 1M)
- **Endpoint**: `POST /get-quotes/`
- **Auth**: Bearer Token
- **Payload**:
```json
{
  "insurance_type": "health",
  "age": 35,
  "sum_insured": 600000,
  "city": "Abu Dhabi",
  "members": 3,
  "nid": "784-1990-1234567-1"
}
```

### 🧪 Scenario C: Premium Global Plan (Sum Insured > 1M)
- **Endpoint**: `POST /get-quotes/`
- **Auth**: Bearer Token
- **Payload**:
```json
{
  "insurance_type": "health",
  "age": 45,
  "sum_insured": 1500000,
  "city": "Dubai",
  "members": 4,
  "nid": "784-1990-1234567-1"
}
```

---

## 3. Motor Insurance (Comparison)
*All motor scenarios use `insurance_type: "motor"`*

### 🚗 Scenario D: Nissan Pathfinder (DIC)
- **Endpoint**: `POST /get-quotes/`
- **Auth**: Bearer Token
- **Payload**:
```json
{
  "insurance_type": "motor",
  "age": 30,
  "sum_insured": 68000,
  "city": "Dubai",
  "members": 1,
  "additional_details": {
    "make": "NISSAN",
    "model": "PATHFINDER",
    "year": 2024
  }
}
```

### 🚗 Scenario E: Toyota Land Cruiser (QIC)
- **Endpoint**: `POST /get-quotes/`
- **Auth**: Bearer Token
- **Payload**:
```json
{
  "insurance_type": "motor",
  "age": 45,
  "sum_insured": 75000,
  "city": "Dubai",
  "members": 1,
  "additional_details": {
    "make": "TOYOTA",
    "model": "LAND CRUISER",
    "year": 2023
  }
}
```

---

## 4. History & Details

### 📜 Get Quote History
- **Endpoint**: `GET /history/`
- **Auth**: Bearer Token

### 🔍 Get Quote Detail
- **Endpoint**: `GET /<quote_request_id>/`
- **Auth**: Bearer Token

---

## 4. Mock External APIs (For Reference)
*These are the internal mock endpoints the backend calls. You can test them directly too.*

- **DIC**: `POST /mock-api/dic-broker-uae/quotes/`
- **QIC**: `POST /mock-api/qic-uae/quotes/`

---

> [!IMPORTANT]
> Ensure the Django server is running via `python manage.py runserver 8000` before starting tests.
