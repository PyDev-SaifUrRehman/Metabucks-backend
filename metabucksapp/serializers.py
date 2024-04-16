from rest_framework import serializers
from .models import ClientUser, Transaction, Referral


class ClientUserSerializer(serializers.ModelSerializer):
    referral_code = serializers.CharField(read_only=True)
    total_deposit = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    total_withdrawal = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    user_type = serializers.BooleanField(required=False)

    class Meta:
        model = ClientUser
        fields = ['wallet_address', 'referral_code', 'balance', 'seven_day_profit',
                  'profit_withdrawl', 'maturity', 'total_deposit', 'total_withdrawal', 'user_type']

    def validate_wallet_address(self, value):
        if ClientUser.objects.filter(wallet_address=value).exists():
            raise serializers.ValidationError("Address already registered!!")
        return value


class ClientWalletDetialSerailizer(serializers.Serializer):
    pass


class AddressToUserField(serializers.RelatedField):
    def to_internal_value(self, value):
        try:
            user = self.queryset.get(wallet_address=value)
            return user
        except self.queryset.model.DoesNotExist:
            raise serializers.ValidationError(
                "User with this wallet address does not exist.")

    def to_representation(self, value):
        return value.wallet_address


class TransactionSerializer(serializers.ModelSerializer):
    sender = AddressToUserField(
        queryset=ClientUser.objects.all())

    class Meta:
        model = Transaction
        fields = ['sender', 'transaction_type',
                  'crypto_name', 'amount', 'timestamp']


class ReferralSerializer(serializers.ModelSerializer):
    commission_earned = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True)
    no_of_referred_users = serializers.IntegerField(read_only=True)
    commission_transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Referral
        fields = ['id', 'user', 'commission_earned',
                  'no_of_referred_users', 'commission_transactions']
