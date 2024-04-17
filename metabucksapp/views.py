from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta
from rest_framework.mixins import ListModelMixin
from django.db import models
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .utils import generate_invitation_code

from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import ClientUser, Referral, Transaction
from metabucksadmin.models import MinimumDeposit, MinimumWithdraw, CommissionUpdate, BaseUser
from .serializers import ClientUserSerializer, ReferralSerializer, TransactionSerializer, ClientWalletDetialSerailizer


class ClientUserViewSet(viewsets.ModelViewSet):
    queryset = ClientUser.objects.all()
    serializer_class = ClientUserSerializer

    def create(self, request):
        ref_code = request.query_params.get('ref')
        if not ref_code:
            return Response({"error": "Referral code is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_with_referral_code = ClientUser.objects.get(
                referral_code=ref_code)
            try:
                referral = user_with_referral_code.referral
            except Referral.DoesNotExist:
                referral = Referral.objects.create(
                    user=user_with_referral_code)
        except ClientUser.DoesNotExist:
            return Response({"error": "Invalid referral code"}, status=status.HTTP_400_BAD_REQUEST)
        new_user_referral_code = generate_invitation_code()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(referral_code=new_user_referral_code)
        user.referred_by = referral
        user.save()
        referral.increase_referred_users()
        serializer_data = serializer.data
        serializer_data['referral_address'] = user.referred_by.user.wallet_address
        return Response(serializer_data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        try:
            wallet_address_from_cookie = request.query_params.get('address')
            instance = ClientUser.objects.get(
                wallet_address=wallet_address_from_cookie)
        except (ObjectDoesNotExist, ValueError):
            return Response({"detail": "User not found or invalid address"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        transactions = instance.transactions.all()
        total_deposit = transactions.filter(transaction_type='Deposit').aggregate(
            total_deposit=models.Sum('amount'))['total_deposit'] or 0
        total_withdrawal = transactions.filter(transaction_type='Withdrawal').aggregate(
            total_withdrawal=models.Sum('amount'))['total_withdrawal'] or 0
        instance.update_balance()
        instance.total_deposit = total_deposit
        instance.total_withdrawal = total_withdrawal
        instance.save()
        return Response(serializer.data)


class UserLoginViewset(viewsets.ViewSet):
    def create(self, request):
        wallet_address = request.query_params.get('address')

        try:
            user = BaseUser.objects.get(wallet_address=wallet_address)

            response = Response({'message': 'Login successful'})
            max_age_30_days = timedelta(days=30)
            response.set_cookie(
                'wallet_address', wallet_address, max_age=max_age_30_days)
            return response
        except ClientUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class GetRefAdressViewset(viewsets.GenericViewSet, ListModelMixin):
    def list(self, request, *args, **kwargs):
        ref_code = request.query_params.get('ref')
        if not ref_code:
            return Response({"error": "Referral code is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_with_referral_code = ClientUser.objects.get(
                referral_code=ref_code)
            return Response({"wallet_address": user_with_referral_code.wallet_address}, status=status.HTTP_200_OK)
        except ClientUser.DoesNotExist:
            return Response({"error": "Invalid referral code"}, status=status.HTTP_400_BAD_REQUEST)


class ClientWalletDetialViewset(viewsets.GenericViewSet, ListModelMixin):

    serializer_class = ClientUserSerializer

    def list(self, request, *args, **kwargs):
        try:
            wallet_address_from_cookie = request.query_params.get('address')
            instance = ClientUser.objects.get(
                wallet_address=wallet_address_from_cookie)
        except (ObjectDoesNotExist, ValueError):
            return Response({"detail": "User not found or invalid address"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        transactions = instance.transactions.all()
        total_deposit = transactions.filter(transaction_type='Deposit').aggregate(
            total_deposit=models.Sum('amount'))['total_deposit'] or 0
        total_withdrawal = transactions.filter(transaction_type='Withdrawal').aggregate(
            total_withdrawal=models.Sum('amount'))['total_withdrawal'] or 0
        maturity = total_deposit*2
        if instance.referred_by != None:
            referrals = instance.referred_by.no_of_referred_users or 0
        else: 
            referrals = 0
        instance.update_balance()
        instance.total_deposit = total_deposit
        instance.total_withdrawal = total_withdrawal
        instance.maturity = maturity
        instance.save()
        serializer_data = serializer.data
        serializer_data['referral'] = referrals
        return Response(serializer_data, status=status.HTTP_200_OK)


class ReferralViewSet(viewsets.ModelViewSet):
    queryset = Referral.objects.all()
    serializer_class = ReferralSerializer

    def list(self, request, pk=None):
        try:
            wallet_address_from_cookie = request.query_params.get('address')
            instance = ClientUser.objects.get(
                wallet_address=wallet_address_from_cookie)
        except (ObjectDoesNotExist, ValueError):
            return Response({"detail": "User not found or invalid address"}, status=status.HTTP_404_NOT_FOUND)

        try:
            referral = Referral.objects.get(user=instance)
        except Referral.DoesNotExist:
            return Response({"error": "Referral not found for this user"}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(referral)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['crypto_name',
                        'sender__wallet_address', 'transaction_type']

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(transaction_type__in=[
                                   'Deposit', 'Withdrawal', 'Referral'])
        wallet_address = self.request.query_params.get('address')
        if wallet_address:
            queryset = queryset.filter(
                sender__wallet_address__in=wallet_address)
        return queryset

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sender = serializer.validated_data.get('sender')
        amount = serializer.validated_data.get('amount')
        crypto_name = serializer.validated_data.get('crypto_name')
        transaction_type = serializer.validated_data.get('transaction_type')

        try:
            referral_commission = CommissionUpdate.objects.get().commission_percentage
        except:
            referral_commission = 0
        referral_commission = amount * referral_commission/100

        try:
            min_deposit = MinimumDeposit.objects.get().amount
        except:
            min_deposit = 0
        try:
            min_withdraw = MinimumWithdraw.objects.get().amount
        except:
            min_withdraw = 0
        if transaction_type == 'Deposit' and amount < min_deposit:
            return Response({'error': f"Minimum amount must be greater than or equal to {min_deposit}"})
        if transaction_type == 'Withdrawal' and amount < min_withdraw:
            return Response({'error': f"Minimum amount must be greater than or equal to {min_withdraw}"})
        sender = ClientUser.objects.get(id=sender.id)
        if transaction_type == 'Deposit' and sender.referred_by:
            referral = sender.referred_by
            referral.increase_commission_earned(referral_commission)
            commission_transaction = Transaction.objects.create(
                sender=referral.user,
                amount=referral_commission,
                crypto_name=crypto_name,
                transaction_type='Referral'
            )
            referral.commission_transactions = commission_transaction

            referral.save()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['get'], detail=False)
    def all_trx(self, request, pk=None):
        try:
            wallet_address_from_cookie = request.query_params.get('address')
            instance = ClientUser.objects.get(
                wallet_address=wallet_address_from_cookie)
        except (ObjectDoesNotExist, ValueError):
            return Response({"detail": "User not found or invalid address"}, status=status.HTTP_404_NOT_FOUND)
        transactions = Transaction.objects.filter(sender=instance)
        serializer = self.get_serializer(transactions, many=True)

        total_deposit = transactions.filter(transaction_type='Deposit').aggregate(
            total_deposit=models.Sum('amount'))['total_deposit'] or 0
        total_withdrawal = transactions.filter(transaction_type='Withdrawal').aggregate(
            total_withdrawal=models.Sum('amount'))['total_withdrawal'] or 0
        response_data = {
            'total_deposit': total_deposit,
            'total_withdrawal': total_withdrawal,
            'transactions': serializer.data
        }
        return Response(response_data)
