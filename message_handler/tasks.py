import datetime
from celery import signals, shared_task
from telegram import Bot

from django.conf import settings

from message_handler import models as message_handler_models


@shared_task()
def send_message_in_telegram(chat_id, message):
    Bot(token=settings.BOT_TOKEN).sendMessage(chat_id=chat_id, text=message)


@shared_task()
def send_scheduled_message_for_subscriber():
    for plan in message_handler_models.SubscribePlan.objects.filter(active=True):
        if plan.updated + datetime.timedelta(seconds=plan.period_in_second) < datetime.datetime.now(
                tz=datetime.timezone.utc):
            plan.send_price_message()
