import datetime

from django.conf import settings

from dani_exchange.celery import app
from dani_exchange.models import Currency, Provider


@app.task(queue=settings.CELERY_QUEUE)
def get_exchange_rates(date=None, provider=None):
    currencies = Currency.objects.all()
    if not date:
        date = datetime.datetime.today().date().strftime('%Y-%m-%d')
    if not provider:
        provider = Provider.objects.all().order_by('-priority').first().name

    for currency in currencies:
        for exchanges_currency in currencies.exclude(code=currency.code):
            Provider.get_exchange_rate_data(currency.code, exchanges_currency.code, date, provider)
