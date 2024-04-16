# Generated by Django 5.0.3 on 2024-04-04 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metabucksadmin', '0002_admintransaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfitUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profit_percentage', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
    ]
