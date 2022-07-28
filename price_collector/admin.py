from django.contrib import admin

from price_collector import models as price_collector_models

admin.site.register(price_collector_models.Market)
