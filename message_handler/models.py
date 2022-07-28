import datetime
from django.db import models

from utils import base as utils_base
from message_handler import tasks as message_handler_task
from message_handler import utils as message_handler_utils


class Subscriber(utils_base.BaseModel):
    chat_id = models.IntegerField(unique=True)


class SubscribePlan(utils_base.BaseModel):
    subscriber = models.ForeignKey(Subscriber, on_delete=models.SET_NULL, null=True)
    markets = models.ManyToManyField('price_collector.Market', blank=True)
    period_in_second = models.PositiveIntegerField()
    active = models.BooleanField(default=True)

    def send_price_message(self):
        self.updated = datetime.datetime.now(tz=datetime.timezone.utc)
        self.save(update_fields=['updated'])
        message = message_handler_utils.create_price_message(markets=self.markets.all())
        message_handler_task.send_message_in_telegram.delay(chat_id=self.subscriber.chat_id, message=message)

