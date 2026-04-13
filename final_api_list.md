# final_api_list

This file documents the complete API surface of the local Promise Insure server for Postman testing.

Base URL: `http://localhost:8000`

> This API suite performs provider quote aggregation, compares results, and returns the final recommended quote with a comparison summary.
>
> The Postman collection is available for import from `Insurance_Quotation_API.postman_collection.json`.

## 1. Authentication

### 1.1 Register User
- Method: `POST`
- URL: `/api/auth/register/`
- Description: Create a new user account and return JWT tokens.
- Request Body:
```json
{
  "username": "testuser",
  "email": "testuser@example.com",
  "password": "Password123!",
  "password2": "Password123!"
}
```
- Expected Success: `201 Created`
- Response Fields:
  - `message`
  - `user` object with `id`, `username`, `email`, `first_name`, `last_name`, `profile`
  - `refresh`
  - `access`

### 1.2 Login
- Method: `POST`
- URL: `/api/auth/login/`
- Description: Authenticate user and receive JWT access + refresh tokens.
- Request Body:
```json
{
  "username": "testuser",
  "password": "Password123!"
}
```
- Expected Success: `200 OK`
- Response Fields:
  - `access`
  - `refresh`
  - `user`

### 1.3 Refresh Token
- Method: `POST`
- URL: `/api/auth/token/refresh/`
- Description: Refresh the access token using a valid refresh token.
- Request Body:
```json
{
  "refresh": "<refresh_token>"
}
```
- Expected Success: `200 OK`
- Response Fields:
  - `access`

### 1.4 Get Profile
- Method: `GET`
- URL: `/api/auth/profile/`
- Description: Retrieve the authenticated user's profile.
- Headers:
  - `Authorization: Bearer <access_token>`
- Expected Success: `200 OK`
- Response Fields:
  - `id`, `username`, `email`, `first_name`, `last_name`, `profile`

### 1.5 Update Profile
- Method: `PUT`
- URL: `/api/auth/profile/`
- Description: Update the authenticated user's profile data.
- Headers:
  - `Authorization: Bearer <access_token>`
- Request Body Examples:
```json
{
  "email": "updated@example.com",
  "first_name": "Test",
  "last_name": "User"
}
```
- Expected Success: `200 OK`
- Response Fields:
  - `message`
  - updated `user`

### 1.6 Change Password
- Method: `POST`
- URL: `/api/auth/change-password/`
- Description: Change password for the authenticated user.
- Headers:
  - `Authorization: Bearer <access_token>`
- Request Body:
```json
{
  "old_password": "Password123!",
  "new_password": "NewPassword123!",
  "new_password2": "NewPassword123!"
}
```
- Expected Success: `200 OK`
- Response Fields:
  - `message`

### 1.7 Logout
- Method: `POST`
- URL: `/api/auth/logout/`
- Description: Invalidate a refresh token.
- Headers:
  - `Authorization: Bearer <access_token>`
- Request Body:
```json
{
  "refresh": "<refresh_token>"
}
```
- Expected Success: `200 OK`
- Response Fields:
  - `message`

## 2. Quote Engine

### 2.1 Fetch Aggregated Quotes
- Method: `POST`
- URL: `/api/quotes/get-quotes/`
- Description: Create a quote request, fetch provider quotes in parallel, compare them, and return the final recommended quote.
- Headers:
  - `Authorization: Bearer <access_token>`
- Request Body:
```json
{
  "insurance_type": "motor",
  "age": 35,
  "sum_insured": 50000,
  "city": "Dubai",
  "members": 1,
  "additional_details": {
    "make": "NISSAN",
    "model": "PATHFINDER",
    "year": 2022
  }
}
```
- Expected Success: `200 OK`
- Response Fields:
  - `best_quote`
  - `quotes` array
  - `comparison_summary`
  - `message`

### 2.2 Get Quote History
- Method: `GET`
- URL: `/api/quotes/history/`
- Description: Retrieve all quote requests for the authenticated user.
- Headers:
  - `Authorization: Bearer <access_token>`
- Expected Success: `200 OK`
- Response Fields:
  - `count`
  - `history` array of quote requests

### 2.3 Get Quote Detail
- Method: `GET`
- URL: `/api/quotes/{quote_request_id}/`
- Description: Retrieve detailed quote request and provider quotes by request ID.
- Headers:
  - `Authorization: Bearer <access_token>`
- Expected Success: `200 OK`
- Response Fields:
  - `quote_request`
  - `best_quote`
  - `all_quotes`
  - `comparison_summary`

### 2.4 Select Scheme
- Method: `POST`
- URL: `/api/quotes/{quote_id}/select-scheme/`
- Description: Select a scheme for a saved quote and simulate provider choice behavior.
- Headers:
  - `Authorization: Bearer <access_token>`
- Request Body:
```json
{
  "covers": {
    "mandatory": "basic",
    "optional": "extended"
  }
}
```
- Expected Success: `200 OK` or `400 Bad Request`
- Response Fields:
  - `message`
  - `payment_url`

### 2.5 Get Policy
- Method: `POST`
- URL: `/api/quotes/{quote_id}/get-policy/`
- Description: Fetch policy details after scheme selection.
- Headers:
  - `Authorization: Bearer <access_token>`
- Request Body:
```json
{
  "quotation_no": "QUOTE12345"
}
```
- Expected Success: `200 OK` or `400 Bad Request`
- Response Fields:
  - `message`
  - `policy_info`
  - `status`

## 3. Mock Provider Simulation Endpoints

These endpoints simulate the external provider APIs used by DIC/QIC during testing.

### 3.1 Provider Quote Simulation
- Method: `POST`
- URL: `/mock-api/{provider_code}/quotes/`
- Description: Simulate a provider quote request.
- Provider examples:
  - `dic`
  - `qic`
- Request Body: provider-specific JSON payload depending on the mock provider.
- Expected Success: `200 OK`

### 3.2 Mock Auth
- Method: `POST`
- URL: `/mock-api/api/v1/User/Auth`
- Description: Simulate provider authentication for mock external providers.
- Request Body Example:
```json
{
  "userName": "MOTOR_USER_001",
  "password": "123456"
}
```
- Expected Success: `200 OK`

### 3.3 Mock Generate Quote
- Method: `POST`
- URL: `/mock-api/api/v1/Insurance/GenerateQuote`
- Description: Simulate provider quote generation for DIC/QIC.
- Request Body: provider-specific payload with policy and customer details.
- Expected Success: `200 OK`

### 3.4 Mock Choose Scheme
- Method: `POST`
- URL: `/mock-api/api/v1/Insurance/ChooseScheme`
- Description: Simulate provider scheme selection behavior.
- Request Body Example:
```json
{
  "prodCode": "PROD001",
  "covers": {
    "mandatory": "basic",
    "optional": "premium"
  }
}
```
- Expected Success: `200 OK`

## 4. Postman Test Flow

1. `POST /api/auth/register/` – create test user
2. `POST /api/auth/login/` – obtain JWT tokens
3. `GET /api/auth/profile/` – verify user details
4. `PUT /api/auth/profile/` – update user details
5. `POST /api/auth/change-password/` – verify password change
6. `POST /api/quotes/get-quotes/` – request quote aggregation and verify final quote comparison output
7. `GET /api/quotes/history/` – confirm quote history
8. `GET /api/quotes/{quote_request_id}/` – review quote details
9. `POST /api/quotes/{quote_id}/select-scheme/` – simulate scheme selection
10. `POST /api/quotes/{quote_id}/get-policy/` – verify policy outcome
11. `POST /mock-api/api/v1/User/Auth` – validate mock auth endpoint
12. `POST /mock-api/api/v1/Insurance/GenerateQuote` – validate mock quote generation
13. `POST /mock-api/api/v1/Insurance/ChooseScheme` – validate mock scheme selection

## 5. Postman Collection

- Import file: `Insurance_Quotation_API.postman_collection.json`
- Use the local file path in Postman to import all request definitions and sample payloads.
- This collection covers registration, login, JWT refresh, quote search, history, detail, scheme selection, and policy endpoints.

## 6. Notes
- Protected API endpoints require `Authorization: Bearer <access_token>`.
- The quote engine stores requests in the database, so history and detail endpoints depend on successful `get-quotes` calls.
- Use `localhost:8000` for local server testing.
