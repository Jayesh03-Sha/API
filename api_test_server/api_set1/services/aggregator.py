from typing import List, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import importlib
from ..models import InsuranceProvider

logger = logging.getLogger(__name__)


class QuoteAggregator:
    """
    Aggregates quotes from multiple insurance providers dynamically loaded from the database.
    Handles parallel API calls and error management.
    """
    
    def __init__(self, providers: List = None):
        """
        Initialize aggregator. If no providers are passed, loads active ones from DB.
        """
        if providers is None:
            self.providers = self._load_active_providers()
        else:
            self.providers = providers
        
        self.max_workers = max(len(self.providers), 1)
    
    def _load_active_providers(self) -> List:
        """
        Loads active providers from the database and instantiates their classes.
        """
        active_providers = InsuranceProvider.objects.filter(is_active=True)
        instances = []
        
        for provider_data in active_providers:
            try:
                # Dynamic import using the class path stored in DB
                module_path, class_name = provider_data.provider_class_path.rsplit('.', 1)
                module = importlib.import_module(module_path)
                provider_class = getattr(module, class_name)
                
                # Instantiate with DB-configured URL and Key
                instance = provider_class(
                    api_key=provider_data.api_key,
                    base_url=provider_data.api_base_url
                )
                instance.provider_name = provider_data.name
                instances.append(instance)
                logger.info(f"Loaded dynamic provider: {provider_data.name}")
                
            except Exception as e:
                logger.error(f"Failed to load provider {provider_data.name}: {str(e)}")
                
        return instances

    def get_all_quotes(self, data: Dict, parallel: bool = True) -> List[Dict]:
        """
        Get quotes from all providers.
        """
        if not self.providers:
            logger.warning("No active providers found in the system.")
            return []

        if parallel:
            return self._get_quotes_parallel(data)
        else:
            return self._get_quotes_sequential(data)
    
    def _get_quotes_sequential(self, data: Dict) -> List[Dict]:
        quotes = []
        for provider in self.providers:
            try:
                quote = provider.get_quote(data)
                if quote:
                    quotes.append(quote)
                    logger.info(f"✓ Quote received from {provider.provider_name}")
                else:
                    logger.warning(f"✗ No quote from {provider.provider_name}")
            except Exception as e:
                logger.error(f"✗ {provider.provider_name} failed: {str(e)}")
        return quotes
    
    def _get_quotes_parallel(self, data: Dict) -> List[Dict]:
        quotes = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_provider = {
                executor.submit(provider.get_quote, data): provider
                for provider in self.providers
            }
            for future in as_completed(future_to_provider):
                provider = future_to_provider[future]
                try:
                    quote = future.result()
                    if quote:
                        quotes.append(quote)
                        logger.info(f"✓ Quote received from {provider.provider_name}")
                    else:
                        logger.warning(f"✗ No quote from {provider.provider_name}")
                except Exception as e:
                    logger.error(f"✗ {provider.provider_name} failed: {str(e)}")
        return quotes
