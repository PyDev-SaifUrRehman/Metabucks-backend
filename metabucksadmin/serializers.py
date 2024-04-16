from rest_framework.exceptions import ValidationError
from metabucksapp.models import Transaction
from metabucksapp.models import ClientUser
from metabucksapp.models import Referral, BaseUser
from rest_framework import serializers
from .models import AdminUser, AdminTransaction, ProfitUpdate, ProtocolFee, CommissionUpdate, MinimumDeposit, MinimumWithdraw, WalletToPool, TopAnnouncement, ManagerUser
from metabucksapp.serializers import ReferralSerializer


class AdminSerializer(serializers.ModelSerializer):
    wallet_address = serializers.CharField(required=True)
    user_type = serializers.CharField(required=False)

    class Meta:
        model = AdminUser
        fields = ['id', 'wallet_address'
                  , 'maturity', 'total_deposit', 'total_withdrawal', 'user_type']

    def validate_wallet_address(self, value):

        if BaseUser.objects.filter(wallet_address=value).exists():
            raise serializers.ValidationError(
                "Wallet address already registered!!")
        return value


class GetAdminSerializer(serializers.ModelSerializer):
    # wallet_address = serializers.CharField(required=True)
    # user_type = serializers.CharField(required=False)

    class Meta:
        model = AdminUser
        fields = ['id', 'wallet_address', 'pool_balance',
                  'payout_balance', 'maturity', 'total_deposit', 'total_withdrawal', 'user_type']

    def validate_wallet_address(self, value):

        if BaseUser.objects.filter(wallet_address=value).exists():
            raise serializers.ValidationError(
                "Wallet address already registered!!")
        return value


# class AddressToAdminUserField(serializers.RelatedField):
#     def to_internal_value(self, value):
#         try:
#             admin_user = self.queryset.get(wallet_address=value)
#             return admin_user
#         except AdminUser.DoesNotExist:
#             raise serializers.ValidationError(
#                 "Admin user with this wallet address does not exist.")

#     def to_representation(self, value):
#         return value.wallet_address


class AdminTransactionSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(read_only=True)

    class Meta:
        model = AdminTransaction
        fields = ['sender', 'transaction_type',
                  'crypto_name', 'amount', 'timestamp']

    def validate(self, attrs):
        wallet_address_from_cookie = self.context['request'].COOKIES.get(
            'wallet_address')
        if wallet_address_from_cookie:
            try:
                admin_user = AdminUser.objects.get(
                    wallet_address=wallet_address_from_cookie)
            except AdminUser.DoesNotExist:
                raise ValidationError(
                    "You don't have permission to perform this action.")

            if admin_user.user_type != 'Admin':
                raise ValidationError(
                    "You don't have permission to perform this action.")
        attrs['sender'] = admin_user
        return attrs


class AdminReferralSerializer(serializers.ModelSerializer):
    referrer = serializers.SerializerMethodField(source='sender')
    referred_by = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['referrer', 'transaction_type',
                  'crypto_name', 'amount', 'timestamp', 'referred_by']

    def get_referrer(self, obj):
        return obj.sender.wallet_address

    def get_referred_by(self, obj):
        try:
            referred_by = obj.sender.referred_by.user.wallet_address
            if referred_by:
                return referred_by
        except:
            return "aaaaaaaa"


class ProfitUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfitUpdate
        fields = ('profit_percentage',)

    def validate(self, attrs):
        wallet_address_from_cookie = self.context['request'].COOKIES.get(
            'wallet_address')
        if wallet_address_from_cookie:
            try:
                admin_user = AdminUser.objects.get(
                    wallet_address=wallet_address_from_cookie)
            except AdminUser.DoesNotExist:
                raise ValidationError(
                    "You don't have permission to perform this action.")

            if admin_user.user_type != 'Admin':
                raise ValidationError(
                    "You don't have permission to perform this action.")
        return attrs


class ProtocolFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProtocolFee
        fields = ('deposit_fee', 'withdraw_fee', 'protocol_fee_wallets')

    def validate_protocol_fee_wallets(self, value):
        if len(value) > 5:
            raise serializers.ValidationError(
                "A maximum of 5 wallet addresses can be added.")
        return value

    def validate(self, attrs):
        wallet_address_from_cookie = self.context['request'].COOKIES.get(
            'wallet_address')
        if wallet_address_from_cookie:
            try:
                admin_user = AdminUser.objects.get(
                    wallet_address=wallet_address_from_cookie)
            except AdminUser.DoesNotExist:
                raise ValidationError(
                    "You don't have permission to perform this action.")

            if admin_user.user_type != 'Admin':
                raise ValidationError(
                    "You don't have permission to perform this action.")
        return attrs


class CommissionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionUpdate
        fields = ('commission_percentage',)

    def validate_commission_percentage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Commission percentage must be between 0 and 100.")
        return value

    def validate(self, attrs):
        wallet_address_from_cookie = self.context['request'].COOKIES.get(
            'wallet_address')
        if wallet_address_from_cookie:
            try:
                admin_user = AdminUser.objects.get(
                    wallet_address=wallet_address_from_cookie)
            except AdminUser.DoesNotExist:
                raise ValidationError(
                    "You don't have permission to perform this action")

            if admin_user.user_type != 'Admin':
                raise ValidationError(
                    "You don't have permission to perform this action")
        return attrs


class MinimumDepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = MinimumDeposit
        fields = ('amount',)

    def validate(self, attrs):
        wallet_address_from_cookie = self.context['request'].COOKIES.get(
            'wallet_address')
        if wallet_address_from_cookie:
            try:
                admin_user = AdminUser.objects.get(
                    wallet_address=wallet_address_from_cookie)
            except AdminUser.DoesNotExist:
                raise ValidationError(
                    "You don't have permission to perform this action")

            if admin_user.user_type != 'Admin':
                raise ValidationError(
                    "You don't have permission to perform this action")
        attrs['sender'] = admin_user
        return attrs


class MinimumWithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = MinimumWithdraw
        fields = ('amount',)

    def validate(self, attrs):
        wallet_address_from_cookie = self.context['request'].COOKIES.get(
            'wallet_address')
        if wallet_address_from_cookie:
            try:
                admin_user = AdminUser.objects.get(
                    wallet_address=wallet_address_from_cookie)
            except AdminUser.DoesNotExist:
                raise ValidationError(
                    "You don't have permission to perform this action")

            if admin_user.user_type != 'Admin':
                raise ValidationError(
                    "You don't have permission to perform this action")
        return attrs


class WalletToPoolSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletToPool
        fields = ('wallet_address', 'deposit_amount', 'maturity_amount')

    def validate(self, attrs):
        wallet_address_from_cookie = self.context['request'].COOKIES.get(
            'wallet_address')
        if wallet_address_from_cookie:
            try:
                admin_user = AdminUser.objects.get(
                    wallet_address=wallet_address_from_cookie)
            except AdminUser.DoesNotExist:
                raise ValidationError(
                    "You don't have permission to perform this action.")

            if admin_user.user_type != 'Admin':
                raise ValidationError(
                    "You don't have permission to perform this action.")
        return attrs


class ManagerSerializer(serializers.ModelSerializer):
    wallet_address = serializers.CharField(required=True)
    user_type = serializers.CharField(required=False)

    class Meta:
        model = ManagerUser
        fields = ['id', 'wallet_address', 'pool_balance',
                  'payout_balance', 'maturity', 'total_deposit', 'total_withdrawal', 'user_type']

    def validate(self, attrs):
        wallet_address_from_cookie = self.context['request'].COOKIES.get(
            'wallet_address')
        print("wal", wallet_address_from_cookie)
        if wallet_address_from_cookie:
            try:
                admin_user = AdminUser.objects.get(
                    wallet_address=wallet_address_from_cookie)
            except AdminUser.DoesNotExist:
                raise ValidationError(
                    "You don't have permission to perform this action.")

            if admin_user.user_type != 'Admin':
                raise ValidationError(
                    "You don't have permission to perform this action.")
        return attrs

    def validate_wallet_address(self, value):

        if BaseUser.objects.filter(wallet_address=value).exists():
            raise serializers.ValidationError(
                "Wallet address already registered!!")
        return value


class TopAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopAnnouncement
        fields = ('announcement_text', 'announcement_link')

    def validate(self, attrs):
        wallet_address_from_cookie = self.context['request'].COOKIES.get(
            'wallet_address')
        if wallet_address_from_cookie:
            try:
                admin_user = AdminUser.objects.get(
                    wallet_address=wallet_address_from_cookie)
            except AdminUser.DoesNotExist:
                raise ValidationError(
                    "You don't have permission to perform this action.")

            if admin_user.user_type != 'Admin':
                raise ValidationError(
                    "You don't have permission to perform this action.")
        return attrs


class AdminManagerSerializer(serializers.Serializer):

    def validate(self, attrs):
        wallet_address_from_cookie = self.context['request'].COOKIES.get(
            'wallet_address')
        if wallet_address_from_cookie:
            try:
                admin_user = AdminUser.objects.get(
                    wallet_address=wallet_address_from_cookie)
            except AdminUser.DoesNotExist:
                raise ValidationError(
                    "You don't have permission to perform this action.")

            if admin_user.user_type != 'Admin':
                raise ValidationError(
                    "You don't have permission to perform this action.")
        return attrs



class GetAdminWallet(serializers.Serializer):
    wallet_address = serializers.CharField( read_only = True)
    user_type = serializers.CharField( read_only = True)
    pool_balance = serializers.DecimalField(max_digits=20, decimal_places=2)
    payout_balance = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_deposit = serializers.DecimalField(max_digits=20, decimal_places=2, read_only = True)
    total_withdrawal = serializers.DecimalField(max_digits=20, decimal_places=2, read_only = True)
    
    class Meta:
        fields = ['wallet_address', 'user_type', 'pool_balance',
                  'payout_balance', 'total_deposit', 'total_withdrawal']

