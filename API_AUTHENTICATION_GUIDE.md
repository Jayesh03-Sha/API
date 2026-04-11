# Authentication API Documentation

## Base URL

```
http://localhost:8080/api/auth/
```

> Note: Some examples use port **8080** and others **8000** — standardize this to one port (prefer 8000 for Django).

---

# Authentication Endpoints

## 1. Register User

**POST** `/api/auth/register/`

Creates a new user account.

### Request Body

```json
{
    "username": "promise",
    "email": "promise@gmail.com",
    "password": "promise@123",
    "password2": "promise@123",
    "first_name": "Promise",
    "last_name": "Insure"
}
```

### Success Response (201)

```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "username": "promise",
        "email": "promise@gmail.com",
        "first_name": "Promise",
        "last_name": "Insure",
        "profile": {
            "phone_number": "+1234567890",
            "organization": "PROMISE INSURE",
            "created_at": "2026-04-06T02:46:08.310476Z"
        }
    },
    "refresh": "<refresh_token>",
    "access": "<access_token>"
}
```

---

## 2. Login

**POST** `/api/auth/login/`

Login using username and password.

### Request Body

```json
{
    "username": "promise",
    "password": "promise@123"
}
```

### Success Response (200)

```json
{
    "refresh": "<refresh_token>",
    "access": "<access_token>",
    "user": {
        "id": 1,
        "username": "promise",
        "email": "promise@gmail.com",
        "first_name": "Promise",
        "last_name": "Insure",
        "profile": {
            "phone_number": "+1234567890",
            "organization": "PROMISE INSURE",
            "created_at": "2026-04-06T02:46:08.310476Z"
        }
    }
}
```

---

## 3. Refresh Access Token

**POST** `/api/auth/token/refresh/`

Get a new access token using a refresh token.

### Request Body

```json
{
    "refresh": "<refresh_token>"
}
```

### Response

```json
{
    "access": "<new_access_token>"
}
```

---

## 4. Get User Profile

**GET** `/api/auth/profile/`

### Headers

```
Authorization: Bearer <access_token>
```

### Response

```json
{
    "id": 1,
    "username": "promise",
    "email": "promise@gmail.com",
    "first_name": "Promise",
    "last_name": "Insure",
    "profile": {
        "phone_number": "+1234567890",
        "organization": "PROMISE INSURE",
        "created_at": "2026-04-06T02:46:08.310476Z"
    }
}
```

---

## 5. Update Profile

**PUT** `/api/auth/profile/`

### Headers

```
Authorization: Bearer <access_token>
```

### Request Body

```json
{
    "email": "promise@gmail.com",
    "first_name": "Promise",
    "last_name": "Insure",
    "phone_number": "+1234567890",
    "organization": "PROMISE INSURE"
}
```

### Response

```json
{
    "message": "Profile updated successfully",
    "user": { ... }
}
```

---

## 6. Change Password

**POST** `/api/auth/change-password/`

### Headers

```
Authorization: Bearer <access_token>
```

### Request Body

```json
{
    "old_password": "promise@123",
    "new_password": "newPassword@456",
    "new_password2": "newPassword@456"
}
```

### Response

```json
{
    "message": "Password changed successfully"
}
```

---

## 7. Logout

**POST** `/api/auth/logout/`

Blacklists refresh token.

### Headers

```
Authorization: Bearer <access_token>
```

### Request Body

```json
{
    "refresh": "<refresh_token>"
}
```

### Response

```json
{
    "message": "Logout successful"
}
```

---

# Error Responses

### 400 Bad Request

```json
{
    "username": ["Username already exists."],
    "email": ["Email already exists."]
}
```

### 401 Unauthorized

```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden

```json
{
    "detail": "You do not have permission to perform this action."
}
```

---

# Authentication Flow (Important)

This is how the system should work:

1. **Register** → Get Access + Refresh token
2. **Login** → Get Access + Refresh token
3. Use **Access token** for authenticated requests
4. When access token expires → Use **Refresh token**
5. **Logout** → Blacklist refresh token

### Token Usage Example

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

# Improvements I Recommend (Very Important)

You should consider adding:

### Add These Endpoints Later

* Email verification
* Forgot password
* Reset password
* Change email
* Upload profile image
* Delete account

### Security Improvements

* Use HttpOnly cookies for tokens
* Add rate limiting on login
* Add email verification
* Add password reset via email
* Enable HTTPS in production
* Token rotation for refresh tokens

---

# Suggested Final Endpoint List (Production Ready)

| Method | Endpoint                   |
| ------ | -------------------------- |
| POST   | /api/auth/register/        |
| POST   | /api/auth/login/           |
| POST   | /api/auth/logout/          |
| POST   | /api/auth/token/refresh/   |
| GET    | /api/auth/profile/         |
| PUT    | /api/auth/profile/         |
| POST   | /api/auth/change-password/ |
| POST   | /api/auth/forgot-password/ |
| POST   | /api/auth/reset-password/  |
| POST   | /api/auth/verify-email/    |

---

# Testing the API

To start the development server:

```bash
cd api_test_server
python manage.py runserver
```

The API will be available at `http://localhost:8080/api/auth/`

You can use tools like:
- **Postman** - Import and test the endpoints
- **curl** - Command-line HTTP client
- **httpie** - User-friendly HTTP client
- **Insomnia** - REST client

---

# Security Notes

1. **JWT Tokens**: Access tokens are short-lived and should be refreshed using the refresh token
2. **Password Requirements**: Passwords must meet Django's password validation requirements
3. **HTTPS**: Use HTTPS in production to protect tokens
4. **Token Storage**: Store tokens securely on the client side (not in localStorage for sensitive apps)
5. **CORS**: Configure CORS settings if the API will be called from a different domain

---

If this is a Django REST + JWT project, I can also help you design:

* Models
* Serializers
* Views
* URLs
* JWT settings
* Full authentication architecture
