from django.contrib import admin

from message_handler import models as message_handler_models

admin.site.register(message_handler_models.Subscriber)
admin.site.register(message_handler_models.SubscribePlan)
