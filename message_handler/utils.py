from decimal import Decimal

from price_collector.redis import TREDIS


def create_price_message(markets):
    message = ''
    for market in markets:
        message += f"🟢 {market} :\n"
        ask_price = TREDIS.redis_instance.get(f"{market}_ask")
        bid_price = TREDIS.redis_instance.get(f"{market}_bid")

        ask_price = Decimal.normalize(Decimal(ask_price)) if float(ask_price) < 1 else format(float(ask_price), ".3f")
        bid_price = Decimal.normalize(Decimal(bid_price)) if float(bid_price) < 1 else format(float(bid_price), ".3f")
        if 'IRT' in str(market):
            message += f"BUY : {bid_price} Toman\n"
            message += f"SELL : {ask_price} Toman\n\n"
        elif 'USDT' in str(market):
            message += f"BUY : {bid_price} $\n"
            message += f"SELL : {ask_price} $\n\n"
    return message
