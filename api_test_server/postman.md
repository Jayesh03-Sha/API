# Complete 5-Step Motor Insurance API Flow

This guide describes how to test the unified 5-step flow for motor insurance procurement via Postman or any HTTP client.

## Pre-requisites
1. **Host**: `http://localhost:8000` (or your active development server)
2. **Auth**: All API endpoints except Registration and Login require a Bearer token.

---

## 1. Auth → Get Token

**Endpoint:** `POST /api/set1/auth/login/`

**Description:** Authenticates a portal user and returns JWT access/refresh tokens.

**Request Body (JSON):**
```json
{
    "username": "testuser",
    "password": "testpassword123"
}
```

**Next Step:** Copy the `access` token from the response and use it as an Authorization Bearer token header for the remaining requests.

---

## 2. Generate Quote → Get Plans

**Endpoint:** `POST /api/set1/quotes/get-quotes/`

**Description:** Submits customer & vehicle data. The system automatically fetches quotations from multiple integrated providers (NIA, DIC, etc.) and compares them.

**Header:** `Authorization: Bearer <your_access_token>`

**Request Body (JSON):**
```json
{
    "insurance_type": "motor",
    "age": 35,
    "sum_insured": 50000,
    "city": "Dubai",
    "members": 1,
    "additional_details": {
        "nid": "784-1990-1234567-1",
        "dob": "1990-01-01",
        "gender": "M",
        "chassis_number": "JHM123456789",
        "reg_number": "DXB-A-123",
        "make_code": "009",
        "model_code": "9195",
        "year": "2023",
        "is_brand_new": false
    }
}
```

**Next Step:** In the response, inside the `quotes` array, pick the desired quote and grab its `id`.

---

## 3. Select Scheme → Get Pricing & Payment URL

**Endpoint:** `POST /api/set1/quotes/<quote_id>/select-scheme/`

**Description:** Selects a specific plan/scheme from a provider and locks in the covers, resulting in a firm quotation number and a fake payment URL for the next step.

**Header:** `Authorization: Bearer <your_access_token>`

**Request Body (JSON):**
```json
{
    "covers": [
        "Agency Repair",
        "Roadside Assistance"
    ]
}
```

**Next Step:** Save the `quotation_no` and the `payment_url`. In a real system, the user is redirected to the `payment_url`.

---

## 4. Payment (External Gateway)

*This step happens outside of the main API scope.* The user completes the transaction via a third-party gateway (e.g. Stripe, Payfort). Upon success, the frontend calls Step 5.

---

## 5. Get Policy → Final Policy Data

**Endpoint:** `POST /api/set1/quotes/<quote_id>/get-policy/`

**Description:** Informs the API that payment is successful. The API calls the provider's finalize/approve endpoints and issues the live policy number and documents.

**Header:** `Authorization: Bearer <your_access_token>`

**Request Body (JSON):**
```json
{
    "quotation_no": "Q/MOT/162428",
    "payment_status": "SUCCESS"
}
```

**Expected Response:**
```json
{
    "message": "Policy generated successfully",
    "policy_no": "POL/MOT/2026/89912",
    "status": "Active"
}
```
