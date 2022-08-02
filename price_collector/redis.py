import redis
import json

from django.conf import settings

from tabdeal.websocket_client import SpotWebsocketClient

from price_collector import models as price_collector_models


class TabdealRedis:
    _REDIS_HOST = settings.REDIS_HOST
    _REDIS_PORT = settings.REDIS_PORT

    def __init__(self):
        self.tabdeal_ws = SpotWebsocketClient()
        self.redis_instance = redis.Redis(host=TabdealRedis._REDIS_HOST, port=TabdealRedis._REDIS_PORT, charset="utf-8",
                                          decode_responses=True)

    def start_wb_for_markets_price(self):
        for market in price_collector_models.Market.objects.all():
            def handler(message):
                try:
                    market_in_message = json.loads(message)['data']["s"]
                    bid_price = json.loads(message)['data']['b'][0][0]
                    ask_price = json.loads(message)['data']['a'][0][0]
                    self.redis_instance.set(f'{market_in_message}_bid', bid_price)
                    self.redis_instance.set(f'{market_in_message}_ask', ask_price)
                except Exception as ve:
                    print(ve)

            self.tabdeal_ws.market_order_book(
                symbol=str(market).lower(),
                id=1,
                callback=handler,
            )

    def close_ws(self):
        self.tabdeal_ws.stop()


TREDIS = TabdealRedis()
