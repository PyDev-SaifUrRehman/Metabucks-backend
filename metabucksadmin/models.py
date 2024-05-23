from django.db import models
from metabucksapp.models import BaseUser

class AdminUser(BaseUser):
    pool_balance = models.PositiveBigIntegerField(default=0)
    payout_balance = models.PositiveBigIntegerField(default=0)

    def save(self, *args, **kwargs):
        self.user_type = 'Admin'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.wallet_address


class AdminTransaction(models.Model):
    
    TRANSACTION_TYPES = [
        ('PoolDeposit', 'PoolDeposit'),
        ('PayoutDeposit', 'PayoutDeposit'),
        ('Withdrawal', 'Withdrawal'),
    ]

    sender = models.ForeignKey(
        AdminUser, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    crypto_name = models.CharField(max_length=256)
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPES)

    def __str__(self):
        return f"{self.sender} : {self.amount}"


# setting
class ProfitUpdate(models.Model):
    profit_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0)


class ProtocolFee(models.Model):
    deposit_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=5)
    withdraw_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=5)
    protocol_fee_wallets = models.JSONField(default=list, blank=True)


class CommissionUpdate(models.Model):
    commission_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=5.0)


class MinimumDeposit(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=50)


class MinimumWithdraw(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=50)


class TopAnnouncement(models.Model):
    announcement_text = models.TextField()
    announcement_link = models.URLField(blank=True, null=True)


# Manager
class ManagerUser(BaseUser):
    pool_balance = models.PositiveBigIntegerField(default=0)
    payout_balance = models.PositiveBigIntegerField(default=0)

    def save(self, *args, **kwargs):
        self.user_type = 'Manager'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.wallet_address
    