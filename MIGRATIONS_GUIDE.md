# 🔄 Database Migrations Guide

## Overview

The quotation system adds two new models to the Django application:
- `QuoteRequest` - Stores user quote requests
- `Quote` - Stores individual provider quotes

This guide walks you through applying these changes.

---

## ⚠️ Important - BEFORE You Migrate

**Backup your database first!** If using SQLite:

```bash
# Navigate to project directory
cd api_test_server

# Backup SQLite database
copy db.sqlite3 db.sqlite3.backup

# Or on Linux/Mac:
# cp db.sqlite3 db.sqlite3.backup
```

---

## 🚀 Running Migrations

### Step 1: Create Migration Files

```bash
cd api_test_server

# Generate migration files based on model changes
python manage.py makemigrations

# Output should show:
# Migrations for 'api_set1':
#   api_set1/migrations/XXXX_auto_YYYYMMDD_HHMM.py
#     - Create model Quote
#     - Create model QuoteRequest
```

### Step 2: Review Migration Files (Optional)

```bash
# Check what changes will be made
python manage.py showmigrations

# Output shows migration status
```

### Step 3: Apply Migrations

```bash
# Apply all pending migrations
python manage.py migrate

# Output should show:
# Running migrations:
#   Applying api_set1.XXXX_auto_YYYYMMDD_HHMM... OK
```

### Step 4: Verify

```bash
# Check if models were created
python manage.py shell

# Inside Python shell:
from api_set1.models import QuoteRequest, Quote
print(QuoteRequest._meta.db_table)  # Should print: api_set1_quoterequest
print(Quote._meta.db_table)         # Should print: api_set1_quote
exit()
```

---

## ✅ Alternative: Direct Migration

If automatic migration doesn't work, manually create migration file:

**File:** `api_set1/migrations/XXXX_create_quote_models.py`

```python
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('api_set1', 'XXXX_previous_migration'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuoteRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('insurance_type', models.CharField(choices=[('health', 'Health Insurance'), ('travel', 'Travel Insurance'), ('motor', 'Motor Insurance'), ('home', 'Home Insurance')], max_length=50)),
                ('age', models.IntegerField()),
                ('sum_insured', models.DecimalField(decimal_places=2, max_digits=12)),
                ('city', models.CharField(max_length=100)),
                ('members', models.IntegerField(default=1)),
                ('additional_details', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quote_requests', to='auth.user')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(choices=[('hdfc', 'HDFC Ergo'), ('icici', 'ICICI Lombard'), ('star', 'Star Health')], max_length=50)),
                ('premium', models.DecimalField(decimal_places=2, max_digits=12)),
                ('coverage', models.DecimalField(decimal_places=2, max_digits=12)),
                ('benefits', models.JSONField(blank=True, default=list)),
                ('comparison_score', models.FloatField(default=0)),
                ('is_best', models.BooleanField(default=False)),
                ('response_time_ms', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('quote_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quotes', to='api_set1.quoterequest')),
            ],
            options={'ordering': ['-comparison_score'], 'unique_together': {('quote_request', 'provider')}},
        ),
    ]
```

Then run:
```bash
python manage.py migrate
```

---

## 🔍 Checking Migration Status

```bash
# See all migrations (applied & pending)
python manage.py showmigrations

# Expected output:
# api_set1
#  [X] 0001_initial
#  [X] 0002_auto_...create_quote_models
#  [X] ... other migrations

# See detailed migration info
python manage.py showmigrations api_set1
```

---

## 🐛 Troubleshooting

### Issue: "No changes detected"

**Solution:** Ensure models were properly edited in `models.py`:

```python
# Check that these classes exist in models.py
class QuoteRequest(models.Model):
    ...

class Quote(models.Model):
    ...
```

Then try again:
```bash
python manage.py makemigrations api_set1
```

### Issue: "django.core.exceptions.ImproperlyConfigured"

**Solution:** Ensure migrations folder has `__init__.py`:

```bash
# Create if missing
touch api_set1/migrations/__init__.py
```

### Issue: Migration naming conflict

**Solution:** Delete the migration file and regenerate:

```bash
# Remove conflicting migration
rm api_set1/migrations/XXXX_auto_...py

# Regenerate
python manage.py makemigrations
```

### Issue: "IntegrityError" during migration

**Solution:** Usually means existing data conflicts. Reset DB (development only):

```bash
# ⚠️ WARNING: This deletes all data
rm db.sqlite3

# Reapply migrations
python manage.py migrate
```

---

## 📊 Database Changes

### New Tables Created

#### `api_set1_quoterequest`
| Field | Type | Notes |
|-------|------|-------|
| id | BigAutoField | Primary key |
| user_id | ForeignKey | Links to auth_user |
| insurance_type | CharField(50) | health, travel, motor, home |
| age | IntegerField | 18-100 |
| sum_insured | DecimalField | Up to 10,000,000 |
| city | CharField(100) | Dubai, Abu Dhabi, etc. |
| members | IntegerField | 1-10 |
| additional_details | JSONField | Extra data |
| created_at | DateTime | Auto-set on creation |
| updated_at | DateTime | Auto-updated |

#### `api_set1_quote`
| Field | Type | Notes |
|-------|------|-------|
| id | BigAutoField | Primary key |
| quote_request_id | ForeignKey | Links to quoterequest |
| provider | CharField(50) | hdfc, icici, star |
| premium | DecimalField | Insurance premium |
| coverage | DecimalField | Coverage amount |
| benefits | JSONField | List of benefits |
| comparison_score | FloatField | 0-100 score |
| is_best | BooleanField | True if best option |
| response_time_ms | IntegerField | API response time |
| created_at | DateTime | Auto-set on creation |

**Indexes:**
- `(quote_request, -comparison_score)` - For sorting quotes
- `provider` - For filtering by provider
- `comparison_score` - For sorting by quality

---

## ✅ Verification Checklist

After migration, verify everything:

```bash
# ✅ Check migration status
python manage.py showmigrations api_set1

# ✅ Verify models exist in database
python manage.py shell
>>> from api_set1.models import QuoteRequest, Quote
>>> QuoteRequest.objects.count()  # Should work (returns 0 initially)
>>> Quote.objects.count()          # Should work (returns 0 initially)
>>> exit()

# ✅ Test models
python manage.py test api_set1.test_quotation.QuoteModelTestCase -v 2

# ✅ Run all tests
python manage.py test api_set1.test_quotation -v 2
```

---

## 🔄 Reverting Migrations (If Needed)

**CAUTION:** This deletes the tables and their data!

```bash
# See all migrations
python manage.py showmigrations

# Revert to specific migration (e.g., revert to 0001_initial)
python manage.py migrate api_set1 0001_initial

# Revert all migrations for api_set1
python manage.py migrate api_set1 zero
```

---

## 📝 Production Deployment Notes

For **PostgreSQL** (recommended in production):

```bash
# Windows
set DATABASE_NAME=promise_insure_db
set DATABASE_USER=postgres
set DATABASE_PASSWORD=your_password
set DATABASE_HOST=localhost

# Linux/Mac
export DATABASE_NAME=promise_insure_db
export DATABASE_USER=postgres
export DATABASE_PASSWORD=your_password
export DATABASE_HOST=localhost

# Then migrate
python manage.py migrate
```

---

## 🆘 Emergency: Database Recovery

If something went wrong:

```bash
# 1. Backup current broken database
copy db.sqlite3 db.sqlite3.broken

# 2. Restore from backup (if you made one earlier)
copy db.sqlite3.backup db.sqlite3

# 3. Reapply migrations
cd api_test_server
python manage.py migrate

# 4. Test
python manage.py test api_set1.test_quotation
```

---

## ✨ Next Steps After Migration

```bash
# 1. Start the server
python manage.py runserver

# 2. Test the API
# Use Postman collection or curl commands

# 3. Create a test user
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.create_user('testuser', 'test@example.com', 'password')
>>> exit()

# 4. Login and get token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password"}'

# 5. Get quotes
curl -X POST http://localhost:8000/api/quotes/get-quotes/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"insurance_type":"health","age":30,"sum_insured":500000,"city":"Dubai","members":2}'
```

---

## 📚 Additional Resources

- Django Migrations: https://docs.djangoproject.com/en/6.0/topics/migrations/
- Database Schema: See models.py in api_set1/
- Migration Commands: `python manage.py help migrate`

---

**Status:** ✅ Migration Ready  
**Version:** 1.0.0  
**Last Updated:** January 2024
