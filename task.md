# Promise Insure API Test Application - Project Task Sheet

## 1. Project Setup
- [x] Create Django project `api_test_server`
- [x] Create Django app `api_set1`
- [x] Configure virtual environment and `requirements.txt`
- [x] Install dependencies: Django, djangorestframework, simplejwt, requests
- [x] Set up `manage.py` and Django settings
- [x] Configure `urls.py` for project and app

## 2. Data Model and Persistence
- [x] Design `QuoteRequest` model to store user requests
- [x] Design `Quote` model to store provider quotes and comparison data
- [x] Add `InsuranceProvider` model for dynamic provider configuration
- [x] Create migrations and apply to database
- [x] Add admin registration for key models

## 3. Authentication
- [x] Add JWT authentication with `djangorestframework-simplejwt`
- [x] Create endpoints for user registration and login
- [x] Create protected endpoints requiring authenticated user
- [x] Validate and save user quote requests with authenticated user context

## 4. Provider Integration
- [x] Create provider base class in `api_set1/services/providers/base.py`
- [x] Implement DIC provider integration in `DIC.py`
- [x] Implement QIC provider integration in `QIC.py`
- [x] Implement NIA provider integration in `NIA.py`
- [x] Add dynamic provider loader in `api_set1/services/aggregator.py`
- [x] Support provider API configuration in database and seed script

## 5. Quote Aggregation and Comparison
- [x] Create `QuoteAggregator` to fetch provider quotes in parallel
- [x] Add sequential fallback behavior and error handling
- [x] Create `QuoteComparator` to score and sort quotes
- [x] Define scoring strategy and comparison summary
- [x] Store comparison results and best quote in database

## 6. API Endpoints and Business Logic
- [x] Build `POST /api/quotes/get-quotes/` endpoint to request all providers
- [x] Add `GET /api/quotes/history/` endpoint for quote history
- [x] Add `GET /api/quotes/{id}/` endpoint for detailed quote request data
- [x] Add select-scheme and get-policy flows for provider-specific quote lifecycle
- [x] Add serializers for request validation and response formatting

## 7. Mock API and Sample Data
- [x] Create `api_test_server/mock_api` views and routes for mocked provider responses
- [x] Add mock JSON/XML files in `API_MOCK_DATA/`
- [x] Add sample request payloads in `API_JSON_FILES/`
- [x] Support DIN/DIC, QIC, and NIA mock behavior for API testing

## 8. Frontend and UI
- [x] Add home page and dashboard templates in `api_test_server/ui/templates/ui/`
- [x] Add admin dashboard and metrics in `api_test_server/ui/views.py`
- [x] Integrate provider and quote summary counts into the UI
- [x] Ensure staff access to dashboard and relevant links

## 9. Testing
- [x] Write unit tests for provider services
- [x] Write tests for aggregator behavior and error handling
- [x] Write comparator tests for scoring logic
- [x] Write API tests for authentication and quote endpoints
- [x] Run tests with Django `manage.py test`

## 10. Deployment Preparation
- [x] Prepare documentation for setup and deployment
- [x] Add implementation guide entries and project summary
- [x] Add Postman collection for API validation
- [x] Validate mock provider endpoint behavior and sample flows
- [x] Confirm database migrations and seed provider data

## 11. Deployment Checklist
- [ ] Configure production database (PostgreSQL or MySQL)
- [ ] Add environment variables for API keys and secrets
- [ ] Secure JWT settings and allowed hosts
- [ ] Configure web server or platform deployment settings
- [ ] Validate static files, templates, and admin access
- [ ] Run full integration tests after deployment

## 12. Recommended Commands
- Setup and migrations:
  ```bash
  cd api_test_server
  python manage.py migrate
  python manage.py createsuperuser
  python manage.py runserver
  ```

- Testing:
  ```bash
  python manage.py test api_set1.test_quotation -v 2
  ```

- Git and deployment:
  ```bash
  git add .
  git commit -m "Project task sheet and final implementation"
  git push origin main
  ```

## 13. Notes
- This task sheet covers the entire project workflow from development through deployment readiness.
- The project is already configured for provider comparison, JWT auth, mock API testing, and admin/UI support.
- Adjust API provider credentials and remote endpoints before production deployment.
