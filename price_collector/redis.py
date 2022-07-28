import redis
import json
from threading import Thread

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

    def start_threads_for_markets_price(self):
        for market in price_collector_models.Market.objects.all():
            Thread(target=self.create_market_socket, args=(str(market),)).start()

    def create_market_socket(self, market):
        def handler(message):
            try:
                bid_price = json.loads(message)['data']['b'][0][0]
                ask_price = json.loads(message)['data']['a'][0][0]
                self.redis_instance.set(f'{market}_bid', bid_price)
                self.redis_instance.set(f'{market}_ask', ask_price)
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
