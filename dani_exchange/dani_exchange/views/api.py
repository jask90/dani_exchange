import datetime
import json

from django.core.serializers.json import DjangoJSONEncoder
from dani_exchange.models import CurrencyExchangeRate
from dani_exchange.serializers import AmountCurrencyExchangeSerializer, CurrencyRatesSerializer, TimeWeightRateSerializer
from dani_exchange.utils import check_exchange_rate_dates
from django.conf import settings
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated


@swagger_auto_schema(methods=['get',], query_serializer=CurrencyRatesSerializer)
@api_view(['GET'])
@authentication_classes((BasicAuthentication, OAuth2Authentication,))
@permission_classes((IsAuthenticated,))
def get_currency_rates(request):
    """
    List of currency rates for a specific time perior
    """
    response = {}

    serializer = CurrencyRatesSerializer(data=request.data)
    if serializer.is_valid():
        try:
            data = serializer.validated_data

            # Check if we have the exchange rates
            check_exchange_rate_dates(data['source_currency'].code, data['date_from'], data['date_to'])

            base_rates = CurrencyExchangeRate.objects.filter(source_currency=data['source_currency'], 
                valuation_date__gte=data['date_from'], valuation_date__lte=data['date_to']).order_by('valuation_date')
        
            dates = list(set(base_rates.values_list('valuation_date', flat=True)))
            for date in dates:
                str_date = date.strftime('%Y-%m-%d')
                response[str_date] = {}
                for rate in base_rates.filter(valuation_date=date):
                    response[str_date][rate.exchanged_currency.code] = round(rate.rate_value, 6)
        except:
            response['errors'] = 'Internal Server Error'
            return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response['errors'] = serializer.errors
        return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), status=status.HTTP_200_OK)


@swagger_auto_schema(methods=['get',], query_serializer=AmountCurrencyExchangeSerializer)
@api_view(['GET'])
@authentication_classes((BasicAuthentication, OAuth2Authentication,))
@permission_classes((IsAuthenticated,))
def calculate_exchange(request):
    """
    Calculates (latest) amount in a currency exchanged into a different currency.
    """
    response = {}

    serializer = AmountCurrencyExchangeSerializer(data=request.data)
    if serializer.is_valid():
        try:
            data = serializer.validated_data
            date = datetime.datetime.now().date()

            # Check if we have the exchange rates
            check_exchange_rate_dates(data['source_currency'].code, date, date)

            cer = CurrencyExchangeRate.objects.filter(source_currency=data['source_currency'], 
                exchanged_currency=data['exchanged_currency'], valuation_date=date).first()
            response['rate'] = cer.rate_value
            response['amount'] = data['amount']
            response['exchange_amount'] = data['amount'] * cer.rate_value
        except:
            response['errors'] = 'Internal Server Error'
            return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        response['errors'] = serializer.errors
        return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), status=status.HTTP_200_OK)


@swagger_auto_schema(methods=['get',], query_serializer=TimeWeightRateSerializer)
@api_view(['GET'])
@authentication_classes((BasicAuthentication, OAuth2Authentication,))
@permission_classes((IsAuthenticated,))
def get_time_weighted_rate(request):
    """
    Service to retrieve time-weighted rate of return for any given amount invested from a currency into another one from given date until today.
    """
    response = {}

    serializer = TimeWeightRateSerializer(data=request.data)
    if serializer.is_valid():
        try:
            data = serializer.validated_data
            today = datetime.datetime.now().date()

            # Check if we have the exchange rates
            check_exchange_rate_dates(data['source_currency'].code, today, today)
            check_exchange_rate_dates(data['source_currency'].code, data['start_date'], data['start_date'])

            today_cer = CurrencyExchangeRate.objects.filter(source_currency=data['source_currency'], 
                exchanged_currency=data['exchanged_currency'], valuation_date=today).first()
            start_cer = CurrencyExchangeRate.objects.filter(source_currency=data['source_currency'], 
                exchanged_currency=data['exchanged_currency'], valuation_date=data['start_date']).first()

            end_amount = (data['amount'] / start_cer.rate_value) * today_cer.rate_value
            twr = (end_amount - data['amount']) / data['amount']

            response['time_weihted_rate'] = round(1 + twr, 6)
            response['time_weihted_rate_percentage'] = round(twr * 100, 6)
            response['initial_rate'] = start_cer.rate_value
            response['end_rate'] = today_cer.rate_value
            response['initial_amount'] = data['amount']
            response['end_amount'] = end_amount
        except:
            response['errors'] = 'Internal Server Error'
            return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        response['errors'] = serializer.errors
        return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), status=status.HTTP_200_OK)
