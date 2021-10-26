import datetime
import logging

from django.db import models

from dani_exchange.providers.fixer import FixerAdapter
from dani_exchange.providers.mock import Mock


logger = logging.getLogger('django')


__all__ = ['CurrencyExchangeRate', 'Currency', 'Provider']


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True, verbose_name=u'code')
    name = models.CharField(max_length=20, db_index=True, verbose_name=u'name')
    symbol = models.CharField(max_length=10, verbose_name=u'symbol')

    class Meta:
        ordering = ['code']
        verbose_name = 'currency'
        verbose_name_plural = 'currencies'

    def __str__(self):
        return f'{self.code} - {self.name}'


class CurrencyExchangeRate(models.Model):
    source_currency = models.ForeignKey(Currency, related_name='exchanges', on_delete=models.CASCADE, verbose_name=u'source currency')
    exchanged_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, verbose_name=u'exchanged currency')
    valuation_date = models.DateField(db_index=True, verbose_name=u'valuation date')
    rate_value = models.DecimalField(db_index=True, decimal_places=6, max_digits=18, verbose_name=u'rate value')

    class Meta:
        ordering = ['valuation_date']
        verbose_name = 'currency exchange rate'
        verbose_name_plural = 'currency exchange rates'

    def __str__(self):
        return f'{self.valuation_date} - {self.source_currency} - {self.exchanged_currency}'


class Provider(models.Model):
    name = models.CharField(max_length=40, unique=True, verbose_name=u'name')
    priority = models.PositiveIntegerField(verbose_name=u'priority')

    class Meta:
        ordering = ['priority']
        verbose_name = 'provider'
        verbose_name_plural = 'providers'

    def __str__(self):
        return f'{self.name} - {self.priority}'

    @staticmethod
    def get_exchange_rate_data(source_currency, exchanged_currency, valuation_date, provider):
        exchange_provider = None
        response = {}
        cer = CurrencyExchangeRate.objects.filter(source_currency__code=source_currency, exchanged_currency__code=exchanged_currency, valuation_date=valuation_date).first()
        if cer: return cer

        if provider == 'Fixer':
            exchange_provider = FixerAdapter()
        elif provider == 'Mock':
            exchange_provider = Mock()

        if exchange_provider:
            response = exchange_provider.get_exchange_rate_data(source_currency, exchanged_currency, valuation_date)

        if response and response['success']:
            try:
                source = Currency.objects.get(code=response['source_currency'])
                exchanged = Currency.objects.get(code=response['exchanged_currency'])
                valuation_date = datetime.datetime.strptime(response['valuation_date'], "%Y-%m-%d").date()
                rate_value = response['rate_value']
                cer = CurrencyExchangeRate.objects.create(source_currency=source, exchanged_currency=exchanged, valuation_date=valuation_date, rate_value=rate_value)
                return cer
            except Exception as e:
                logger.error(e)
                return None
        else:
            logger.error(response)
            return None
