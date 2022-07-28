from celery import shared_task
from celery import signals

from price_collector.redis import TREDIS


@signals.worker_ready.connect
def update_tabdeal_price_in_redis(**kwargs):
    TREDIS.start_threads_for_markets_price()
