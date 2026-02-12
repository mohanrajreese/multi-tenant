import logging
from decimal import Decimal
from typing import Dict

logger = logging.getLogger(__name__)

class CurrencyConversionService:
    """
    Tau Tier: Global Currency Conversion Engine.
    Handles exchange rate logic for localized billing.
    """
    
    # Mock exchange rates (Base: USD)
    _rates: Dict[str, Decimal] = {
        "USD": Decimal("1.0"),
        "EUR": Decimal("0.92"),
        "GBP": Decimal("0.79"),
        "INR": Decimal("83.0"),
        "JPY": Decimal("150.0")
    }

    @classmethod
    def convert(cls, amount: float, from_currency: str, to_currency: str) -> float:
        """
        Converts an amount between two currencies.
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if from_currency == to_currency:
            return float(amount)

        if from_currency not in cls._rates or to_currency not in cls._rates:
            logger.error(f"Unsupported currency conversion: {from_currency} -> {to_currency}")
            return float(amount)

        # conversion: (amount / from_rate) * to_rate
        base_amount = Decimal(str(amount)) / cls._rates[from_currency]
        converted = base_amount * cls._rates[to_currency]
        
        return float(round(converted, 2))

    @classmethod
    def get_supported_currencies(cls):
        return list(cls._rates.keys())
