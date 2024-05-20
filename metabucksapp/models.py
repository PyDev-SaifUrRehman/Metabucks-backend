from django.db import models

class BaseUser(models.Model):

    USER_TYPE_CHOICES = [
        ('Client', 'Client'),
        ('Admin', 'Admin'),
        ('Manager', 'Manager'),
    ]

    wallet_address = models.CharField(max_length=100)
    maturity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deposit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    total_withdrawal = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    user_type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES)
    admin_added_deposit  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    admin_maturity  = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    admin_added_withdrawal  = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self) -> str:
        return self.wallet_address


class ClientUser(BaseUser):

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    referral_code = models.CharField(max_length=100, unique=True)
    referred_by = models.ForeignKey(
        'Referral', on_delete=models.SET_NULL, null=True, blank=True, related_name='referred_user')
    seven_day_profit = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    profit_withdrawl = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.user_type = 'Client'
        super().save(*args, **kwargs)

    def update_balance(self):
        try:
            referral = self.referral
            print("reee", referral)
            if referral:
                self.balance = self.seven_day_profit + referral.commission_earned
            else:
                self.balance = self.seven_day_profit
            print("blnce", self.balance)
            self.save()
        except:
            pass

    def __str__(self):
        return self.wallet_address


class Referral(models.Model):
    user = models.ForeignKey(
        ClientUser, on_delete=models.CASCADE, related_name='referral')
    commission_transactions = models.ForeignKey(
        'Transaction', on_delete=models.CASCADE, blank=True, null=True, related_name='referral_trx')
    no_of_referred_users = models.PositiveIntegerField(default=0)
    commission_earned = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    commission_received = models.BooleanField(default=False)

    def increase_referred_users(self):
        self.no_of_referred_users += 1
        self.save()

    def increase_commission_earned(self, amount):
        self.commission_earned += amount
        self.save()

    def mark_commission_received(self):
        self.commission_received = True
        self.save()

    def __str__(self):
        return str(self.user)


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('Deposit', 'Deposit'),
        ('Withdrawal', 'Withdrawal'),
        ('Referral', 'Referral'),
    ]

    sender = models.ForeignKey(
        ClientUser, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    crypto_name = models.CharField(max_length=256)
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPES)

    def __str__(self):
        return f"{self.sender} : {self.amount}"
