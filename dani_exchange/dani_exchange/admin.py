from django.contrib import admin
from dani_exchange.models import *


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'symbol',]
    ordering = ['code', 'name',]
    search_fields = ['code', 'name',]


class CurrencyExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['source_currency', 'exchanged_currency', 'valuation_date', 'rate_value',]
    ordering = ['source_currency', 'exchanged_currency', 'valuation_date', 'rate_value',]
    list_filter = ['source_currency', 'exchanged_currency',]
    search_fields = ['source_currency',]


class ProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'priority',]
    ordering = ['name', 'priority',]
    search_fields = ['name',]


admin.site.register(Currency, CurrencyAdmin)
admin.site.register(CurrencyExchangeRate, CurrencyExchangeRateAdmin)
admin.site.register(Provider, ProviderAdmin)
