# Generated by Django 5.0.3 on 2024-04-05 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metabucksadmin', '0004_alter_profitupdate_profit_percentage'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommissionUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commission_percentage', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='MinimumDeposit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='MinimumWithdraw',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='ProtocolFee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deposit_fee', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('withdraw_fee', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('protocol_fee_wallets', models.JSONField(blank=True, default=list)),
            ],
        ),
        migrations.CreateModel(
            name='TopAnnouncement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('announcement_text', models.TextField()),
                ('announcement_link', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WalletToPool',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wallet_address', models.CharField(max_length=100)),
                ('deposit_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('maturity_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
        ),
    ]
