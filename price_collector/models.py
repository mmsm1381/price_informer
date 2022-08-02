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

    class Meta:
        unique_together = ['first_currency_symbol', 'second_currency_symbol', 'exchange']

    def __str__(self):
        return f"{self.first_currency_symbol}_{self.second_currency_symbol}"

    @classmethod
    def get_all_markets_from_tabdeal(cls):
        markets = json.loads(requests.get(settings.TABDEAL_URLS['market_information']).content)
        for market in markets:
            first_symbol, second_symbol = market['symbol'].split('_')
            cls.objects.get_or_create(first_currency_symbol=first_symbol, second_currency_symbol=second_symbol,
                                      exchange=cls.Exchange.Tabdeal)

    @classmethod
    def get_all_markets_from_db_and_create_message(cls):
        message = ''
        for market in cls.objects.all():
            message += f"🟢 {market}\n"
        return message
