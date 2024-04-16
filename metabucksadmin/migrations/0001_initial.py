# Generated by Django 5.0.3 on 2024-04-03 10:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('metabucksapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminUser',
            fields=[
                ('baseuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='metabucksapp.baseuser')),
                ('pool_balance', models.PositiveBigIntegerField(default=0)),
                ('payout_balance', models.PositiveBigIntegerField(default=0)),
            ],
            bases=('metabucksapp.baseuser',),
        ),
    ]
