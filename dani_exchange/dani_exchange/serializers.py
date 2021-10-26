from rest_framework import serializers
from dani_exchange.models import Currency


class CurrencyField(serializers.RelatedField):
    def get_queryset(self):
        return Currency.objects.all()

    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        try:
            currency = Currency.objects.get(code=data)
        except:
            raise serializers.ValidationError(f'Currency not found {data}')
        return currency


class CurrencyRatesSerializer(serializers.Serializer):
    source_currency = CurrencyField()
    date_from = serializers.DateField()
    date_to = serializers.DateField()


class AmountCurrencyExchangeSerializer(serializers.Serializer):
    source_currency = CurrencyField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    exchanged_currency = CurrencyField()


class TimeWeightRateSerializer(serializers.Serializer):
    source_currency = CurrencyField()
    exchanged_currency = CurrencyField()
    start_date = serializers.DateField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
