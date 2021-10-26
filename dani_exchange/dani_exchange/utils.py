from datetime import timedelta

from dani_exchange.models import CurrencyExchangeRate
from dani_exchange.tasks import get_exchange_rates


def check_exchange_rate_dates(currency, date_from, date_to):
    date = date_from
    delta = date_to - date_from

    if not CurrencyExchangeRate.objects.filter(source_currency__code=currency, valuation_date=date).exists():
        get_exchange_rates(date=date.strftime('%Y-%m-%d'))
    for i in range(delta.days + 1):
        date = date_from + timedelta(days=i)

        if not CurrencyExchangeRate.objects.filter(source_currency__code=currency, valuation_date=date).exists():
            get_exchange_rates(date=date.strftime('%Y-%m-%d'))
