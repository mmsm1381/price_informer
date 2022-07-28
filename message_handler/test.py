from tabdeal.websocket_client import SpotWebsocketClient


def handler(message):
    print(message)


tabdeal_ws = SpotWebsocketClient()

tabdeal_ws.market_order_book(
    symbol="manairt",
    id=1,
    callback=handler,
)
