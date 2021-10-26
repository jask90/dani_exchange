import json

from django.contrib.auth.models import User
from dani_exchange.models import *
from oauth2_provider.models import Application
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
import datetime


class AvailabilityTestCase(TestCase):

    def setUp(self):
        user = User(username='api_test')
        user.set_password('cyPNjhx9aNADjF4Z')
        user.save()
        application = Application.objects.create(user=user, authorization_grant_type='password', client_type='confidential', name='api_test')
        eur = Currency.objects.create(code='EUR', name='Euro', symbol='Є')
        dollar = Currency.objects.create(code='USD', name='Dollar', symbol='$')
        CurrencyExchangeRate.objects.create(source_currency=eur, exchanged_currency=dollar, valuation_date=datetime.datetime(2021, 10, 25).date(), rate_value=1.16)
        CurrencyExchangeRate.objects.create(source_currency=eur, exchanged_currency=dollar, valuation_date=datetime.datetime(2021, 10, 26).date(), rate_value=1.15)
        CurrencyExchangeRate.objects.create(source_currency=dollar, exchanged_currency=eur, valuation_date=datetime.datetime(2021, 10, 25).date(), rate_value=0.86)
        CurrencyExchangeRate.objects.create(source_currency=dollar, exchanged_currency=eur, valuation_date=datetime.datetime(2021, 10, 26).date(), rate_value=0.87)
        Provider.objects.create(name='Mock', priority=100)

        client = APIClient()

        data = {'grant_type': application.authorization_grant_type, 'username': user.username, 'password': 'cyPNjhx9aNADjF4Z', 'client_id': application.client_id, 'client_secret':  application.client_secret}

        response = client.post('/oauth2/access_token/', data)

        result = json.loads(response.content)
        self.access_token = result['access_token']
        self.user = user

    def test_get_currency_rates(self):
        client = APIClient()
        client.force_authenticate(user=self.user, token=self.access_token)

        expected_response = {
            '2021-10-25': {'USD': '1.160000'},
            '2021-10-26': {'USD': '1.150000'}
            }

        data = {'source_currency': 'EUR', 'date_from': '2021-10-25', 'date_to': '2021-10-26'}

        response = client.generic(method='POST', path=f'/api/currency_rates/', data=json.dumps(data), content_type='application/json')

        result = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(result, expected_response)
    
    def test_calculate_exchange(self):
        client = APIClient()
        client.force_authenticate(user=self.user, token=self.access_token)

        expected_response = {'rate': '1.150000', 'amount': '10.50', 'exchange_amount': '12.07500000'}

        data = {'source_currency': 'EUR', 'amount': 10.50, 'exchanged_currency': 'USD'}

        response = client.generic(method='POST', path=f'/api/calculate_exchange/', data=json.dumps(data), content_type='application/json')

        result = json.loads(response.content)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(result, expected_response)

    def test_get_time_weighted_rate(self):
        client = APIClient()
        client.force_authenticate(user=self.user, token=self.access_token)

        expected_response = {
            'end_amount': '1011.627906976744186046511628',
            'end_rate': '0.870000',
            'initial_amount': '1000.00',
            'initial_rate': '0.860000',
            'time_weihted_rate': '1.011628',
            'time_weihted_rate_percentage': '1.162791'
            }

        data = {'source_currency': 'USD', 'exchanged_currency': 'EUR', 'start_date': '2021-10-25', 'amount': 1000}

        response = client.generic(method='POST', path=f'/api/time_weighted_rate/', data=json.dumps(data), content_type='application/json')

        result = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(result, expected_response)