# Generated by Django 4.0.6 on 2022-07-26 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Market',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_currency_symbol', models.CharField(max_length=32)),
                ('second_currency_symbol', models.CharField(max_length=32)),
                ('tabdeal_price', models.DecimalField(decimal_places=16, max_digits=16, max_length=32, null=True)),
            ],
            options={
                'unique_together': {('first_currency_symbol', 'second_currency_symbol')},
            },
        ),
    ]