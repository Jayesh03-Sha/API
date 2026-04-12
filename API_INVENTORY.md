# 🚀 Project API Inventory

This document provides a comprehensive list of all API endpoints available in the **Promise Insurance Services** project.

## Authentication Endpoints
All authentication endpoints are prefixed with `/api/auth/`.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/auth/register/` | Register a new user account | No |
| `POST` | `/api/auth/login/` | Authenticate user and receive JWT tokens | No |
| `POST` | `/api/auth/token/refresh/` | Refresh expired access tokens | No |
| `GET`  | `/api/auth/profile/` | Retrieve current user profile details | **Yes (JWT)** |
| `POST` | `/api/auth/change-password/` | Update user password | **Yes (JWT)** |
| `POST` | `/api/auth/logout/` | Blacklist refresh token and logout | **Yes (JWT)** |

## Insurance Quotation Endpoints
All quotation endpoints are prefixed with `/api/quotes/`.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/quotes/get-quotes/` | **Main Engine**: Fetch parallelquotes&compare| **Yes (JWT)** |
| `GET`  | `/api/quotes/history/` | View user's quote request history | **Yes (JWT)** |
| `GET`  | `/api/quotes/<id>/` | View specific quote details and scores | **Yes (JWT)** |

## Administrative
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `ANY`  | `/admin/` | Django Administrative Interface | Yes (Staff) |

---
*Generated on 2026-04-08*
