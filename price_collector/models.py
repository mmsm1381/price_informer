import json
import requests

from django.conf import settings
from django.db import models

from utils import base as utils_base


class Market(utils_base.BaseModel):
    class Exchange(models.IntegerChoices):
        Tabdeal = 1

    first_currency_symbol = models.CharField(max_length=32)
    second_currency_symbol = models.CharField(max_length=32)
    exchange = models.SmallIntegerField(choices=Exchange.choices)
    bids_price = models.DecimalField(decimal_places=16, max_length=32, null=True, max_digits=16)
    asks_price = models.DecimalField(decimal_places=16, max_length=32, null=True, max_digits=16)

    class Meta:
        unique_together = ['first_currency_symbol', 'second_currency_symbol']

    def __str__(self):
        return f"{self.first_currency_symbol}{self.second_currency_symbol}"

    @classmethod
    def get_all_markets_from_tabdeal(cls):
        markets = json.loads(requests.get(settings.TABDEAL_URLS['market_information']).content)
        for market in markets:
            first_symbol, second_symbol = market['symbol'].split('_')
            cls.objects.get_or_create(first_currency_symbol=first_symbol, second_currency_symbol=second_symbol,
                                      exchange=cls.Exchange.Tabdeal)
