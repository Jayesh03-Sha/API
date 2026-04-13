import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_test_server.settings')
django.setup()

from api_set1.models import InsuranceProvider

def seed_providers():
    dic_api_base_url = os.environ.get('DIC_API_BASE_URL', 'http://localhost:8000/mock-api/')
    dic_api_key = os.environ.get('DIC_API_KEY', 'dic_uae_test_key_001')
    qic_api_base_url = os.environ.get('QIC_API_BASE_URL', 'http://localhost:8000/mock-api/qic-uae/')
    qic_api_key = os.environ.get('QIC_API_KEY', 'qic_uae_test_key_002')
    nia_api_base_url = os.environ.get('NIA_API_BASE_URL', 'http://localhost:8000/mock-api/nia/')
    nia_api_key = os.environ.get('NIA_API_KEY', 'nia_uae_test_key_003')

    providers = [
        {
            "name": "DIC Insurance Broker UAE",
            "code": "dic-broker-uae",
            "api_base_url": dic_api_base_url,
            "api_key": dic_api_key,
            "provider_class_path": "api_set1.services.providers.DIC.DICProvider",
            "icon_name": "fas fa-handshake"
        },
        {
            "name": "QIC Insurance UAE",
            "code": "qic-uae",
            "api_base_url": qic_api_base_url,
            "api_key": qic_api_key,
            "provider_class_path": "api_set1.services.providers.QIC.QICProvider",
            "icon_name": "fas fa-shield-alt"
        },
        {
            "name": "NIA Insurance UAE",
            "code": "nia-uae",
            "api_base_url": nia_api_base_url,
            "api_key": nia_api_key,
            "provider_class_path": "api_set1.services.providers.NIA.NIAProvider",
            "icon_name": "fas fa-certificate"
        }
    ]

    for p_data in providers:
        obj, created = InsuranceProvider.objects.get_or_create(
            code=p_data['code'],
            defaults=p_data
        )
        if created:
            print(f"Created provider: {p_data['name']}")
        else:
            print(f"Provider already exists: {p_data['name']}")

if __name__ == "__main__":
    seed_providers()
