import datetime
import json
import random

import requests
from django.conf import settings


class Mock:

    def get_exchange_rate_data(self, source_currency, exchanged_currency, valuation_date):
        response = {}
        response['success'] = True
        response['valuation_date'] = valuation_date
        response['source_currency'] = source_currency
        response['exchanged_currency'] = exchanged_currency
        response['rate_value'] = round(random.uniform(settings.MOCK_PROVIDER_MIN, settings.MOCK_PROVIDER_MAX), 6)
        return response
