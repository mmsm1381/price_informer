# Generated by Django 4.0.6 on 2022-07-26 20:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('price_collector', '0003_market_created_market_updated'),
        ('message_handler', '0002_remove_subscriber_email_subscriber_active_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subscriber',
            name='active',
        ),
        migrations.AddField(
            model_name='subscriber',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subscriber',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.CreateModel(
            name='SubscribePlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('period_in_second', models.PositiveIntegerField()),
                ('active', models.BooleanField(default=True)),
                ('markets', models.ManyToManyField(blank=True, to='price_collector.market')),
                ('subscriber', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='message_handler.subscriber')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]