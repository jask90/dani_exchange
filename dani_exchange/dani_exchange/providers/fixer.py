import datetime
import json

import requests
from django.conf import settings


class Fixer:

    def __init__(self, *args, **kwargs):
        self.key = settings.FIXER_KEY
        self.base_url = settings.FIXER_BASE_URL

    def get_historical_rate(self, source_currency, exchanged_currency, valuation_date):
        response = {}

        try:
            datetime.datetime.strptime(valuation_date, "%Y-%m-%d")
        except:
            response['error'] = 'valuation_date bad format'
            response['success'] = False
            return response

        url = f'{self.base_url}{valuation_date}?access_key={self.key}&base={source_currency}&symbols={exchanged_currency}'
        req = requests.post(url)

        try:
            content = json.loads(req.content)
            return content
        except:
            response['error'] = f'Response cant be decode'
            response['success'] = False
            return response


class FixerAdapter(Fixer):

    def get_exchange_rate_data(self, source_currency, exchanged_currency, valuation_date):
        adapter_resp = {}
        base_currency = settings.BASE_CURRENCY_CODE
        other_currency = ''

        if source_currency != settings.BASE_CURRENCY_CODE and exchanged_currency != settings.BASE_CURRENCY_CODE:
            other_currency = f'{source_currency},{exchanged_currency}'
        elif source_currency != settings.BASE_CURRENCY_CODE:
            other_currency = source_currency
        else:
            other_currency = exchanged_currency

        response = self.get_historical_rate(base_currency, other_currency, valuation_date)

        if response['success']:
            adapter_resp['success'] = response['success']
            adapter_resp['valuation_date'] = response['date']
            adapter_resp['source_currency'] = source_currency
            adapter_resp['exchanged_currency'] = exchanged_currency
            if source_currency != settings.BASE_CURRENCY_CODE and exchanged_currency != settings.BASE_CURRENCY_CODE:
                source_rate = response['rates'][source_currency]
                exchanged_rate = response['rates'][exchanged_currency]
                adapter_resp['rate_value'] = (1 / source_rate) * exchanged_rate
            elif source_currency != settings.BASE_CURRENCY_CODE:
                adapter_resp['rate_value'] = 1 / response['rates'][source_currency]
            else:
                # source_currency == settings.BASE_CURRENCY_CODE
                adapter_resp['rate_value'] = response['rates'][exchanged_currency]
        else:
            adapter_resp = response

        return adapter_resp
