from typing import List, Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class QuoteComparator:
    """
    Compares and scores insurance quotes using intelligent algorithms.
    Provides best quote selection and ranking.
    """
    
    # Scoring weights (must sum to 1.0)
    WEIGHT_PREMIUM = 0.40      # 40% - Lower premium = better
    WEIGHT_BENEFITS = 0.30     # 30% - More benefits = better
    WEIGHT_COVERAGE = 0.15     # 15% - Higher coverage = better
    WEIGHT_CLAIM_SETTLEMENT = 0.10  # 10% - Higher ratio = better
    WEIGHT_NETWORK = 0.05      # 5% - Larger network = better
    
    def __init__(self):
        """Initialize quote comparator"""
        self._validate_weights()
    
    def _validate_weights(self):
        """Validate that weights sum to 1.0"""
        total = (
            self.WEIGHT_PREMIUM +
            self.WEIGHT_BENEFITS +
            self.WEIGHT_COVERAGE +
            self.WEIGHT_CLAIM_SETTLEMENT +
            self.WEIGHT_NETWORK
        )
        assert abs(total - 1.0) < 0.01, "Scoring weights must sum to 1.0"
    
    def compare_quotes(self, quotes: List[Dict]) -> Tuple[Optional[Dict], List[Dict]]:
        """
        Compare and score quotes, returning best quote and ranked list.
        
        Args:
            quotes: List of quotes to compare
            
        Returns:
            Tuple of (best_quote, all_quotes_sorted_by_score)
        """
        if not quotes:
            return None, []
        
        # Calculate scores for all quotes
        for quote in quotes:
            quote['score'] = self._calculate_score(quote)
        
        # Sort by score descending
        sorted_quotes = sorted(quotes, key=lambda x: x['score'], reverse=True)
        
        # Mark best quote
        if sorted_quotes:
            sorted_quotes[0]['is_best'] = True
        
        best_quote = sorted_quotes[0] if sorted_quotes else None
        
        logger.info(f"Quote comparison complete. Best: {best_quote['provider']} (Score: {best_quote['score']:.2f})")
        
        return best_quote, sorted_quotes
    
    def _calculate_score(self, quote: Dict) -> float:
        """
        Calculate comprehensive score for a quote.
        
        Scoring formula:
        - Premium: Inversely proportional (lower = higher score)
        - Benefits: Number of benefits (more = higher score)
        - Coverage: Directly proportional (higher = higher score)
        - Claim Settlement: Directly proportional (higher ratio = higher score)
        - Network: Directly proportional (larger = higher score)
        
        Args:
            quote: Quote dictionary
            
        Returns:
            Composite score (0-100)
        """
        score = 0.0
        
        # 1. Premium Score (lower premium = higher score)
        # Normalize: max 10000 premium = 100 points
        premium = float(quote.get('premium', 10000))
        premium_score = max(0, (10000 - premium) / 100)
        premium_score = min(100, premium_score)  # Cap at 100
        score += premium_score * self.WEIGHT_PREMIUM
        
        # 2. Benefits Score (more benefits = higher score)
        # Each benefit worth ~20 points (5 benefits = 100 points)
        benefits = quote.get('benefits', [])
        benefits_score = min(100, len(benefits) * 20)
        score += benefits_score * self.WEIGHT_BENEFITS
        
        # 3. Coverage Score (higher coverage = higher score)
        # Normalize: max 10000000 coverage = 100 points
        coverage = float(quote.get('coverage', 500000))
        coverage_score = min(100, (coverage / 100000))
        score += coverage_score * self.WEIGHT_COVERAGE
        
        # 4. Claim Settlement Ratio Score (if available)
        # Directly use the percentage if provided
        claim_ratio = quote.get('claim_settlement_ratio', 90)
        if claim_ratio and isinstance(claim_ratio, (int, float)):
            score += claim_ratio * self.WEIGHT_CLAIM_SETTLEMENT
        
        # 5. Network Score (larger network = higher score)
        # For hospitals: every 1000 hospitals = 10 points
        network = quote.get('network_hospitals', 5000)
        if network and isinstance(network, (int, float)):
            network_score = min(100, (network / 1000) * 10)
            score += network_score * self.WEIGHT_NETWORK
        
        return round(score, 2)
    
    def get_comparison_summary(self, quotes: List[Dict]) -> Dict:
        """
        Get summary statistics about the quotes.
        
        Args:
            quotes: List of quotes
            
        Returns:
            Summary dictionary with averages and ranges
        """
        if not quotes:
            return {}
        
        premiums = [float(q.get('premium', 0)) for q in quotes]
        scores = [q.get('score', 0) for q in quotes]
        
        return {
            'count': len(quotes),
            'avg_premium': round(sum(premiums) / len(premiums), 2),
            'min_premium': round(min(premiums), 2),
            'max_premium': round(max(premiums), 2),
            'premium_range': round(max(premiums) - min(premiums), 2),
            'avg_score': round(sum(scores) / len(scores), 2),
            'highest_score': round(max(scores), 2),
        }
