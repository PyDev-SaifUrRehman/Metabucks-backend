from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from rest_framework import filters, viewsets, status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import ClientUser, Referral, Transaction
from .serializers import ClientUserSerializer, ReferralSerializer, TransactionSerializer, ClientWalletDetialSerailizer
from .utils import generate_invitation_code
from metabucksadmin.models import MinimumDeposit, MinimumWithdraw, CommissionUpdate, BaseUser


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
                referral = Referral.objects.create(
                    user=user_with_referral_code)
            except Referral.DoesNotExist:
                return Response({"error": "Error to create ref."})
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
            instance = ClientUser.objects.select_related('referred_by').prefetch_related('transactions').get(wallet_address=wallet_address_from_cookie)

        except (ObjectDoesNotExist, ValueError):
            return Response({"detail": "User not found or invalid address"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        instance.update_balance()
        try:
            referrals = Referral.objects.filter(user=instance)
            total_referred_users = referrals.aggregate(total_users=models.Sum('no_of_referred_users'))['total_users'] or 0

        except: 
            referrals = 0
        instance.update_balance()
        serializer_data = serializer.data
        serializer_data['referral'] = total_referred_users
        return Response(serializer_data, status=status.HTTP_200_OK)        


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
            instance = ClientUser.objects.select_related('referred_by').prefetch_related('transactions').get(wallet_address=wallet_address_from_cookie)

        except (ObjectDoesNotExist, ValueError):
            return Response({"detail": "User not found or invalid address"}, status=status.HTTP_404_NOT_FOUND)

        try:
            referrals = Referral.objects.filter(user=instance)
            total_referred_users = referrals.aggregate(total_users=models.Sum('no_of_referred_users'))['total_users'] or 0

        except: 
            referrals = 0
        instance.update_balance()
        instance.save()
        serializer = self.get_serializer(instance)
        serializer_data = serializer.data
        serializer_data['referral'] = total_referred_users
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
            referrals = Referral.objects.filter(user=instance)
        except Referral.DoesNotExist:
            return Response({"error": "Referral not found for this user"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(referrals, many = True)
        total_referred_users = referrals.aggregate(total_users=models.Sum('no_of_referred_users'))['total_users'] or 0
        total_commission_earned = referrals.aggregate(total_commission=models.Sum('commission_earned'))['total_commission'] or 0
        
        return Response({"no_of_referred_users": total_referred_users,
            "commission_earned": total_commission_earned})


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all().select_related('sender')

    serializer_class = TransactionSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['crypto_name', 'sender__wallet_address',
                        'sender__referred_by__user__wallet_address', 'transaction_type']

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(transaction_type__in=[
                                   'Deposit', 'Withdrawal', 'Referral', 'Transfer'])
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
            referral_commission = 5
        referral_commission = amount * referral_commission/100

        try:
            min_deposit = MinimumDeposit.objects.get().amount
        except:
            min_deposit = 50
        try:
            min_withdraw = MinimumWithdraw.objects.get().amount
        except:
            min_withdraw = 50
        if transaction_type == 'Deposit' and amount < min_deposit:
            return Response({'error': f"Minimum amount must be greater than or equal to {min_deposit}"})
        if transaction_type == 'Withdrawal' and amount < min_withdraw:
            return Response({'error': f"Minimum amount must be greater than or equal to {min_withdraw}"})
        sender = ClientUser.objects.get(id=sender.id)
        if transaction_type == 'Deposit':
            
            if sender.referred_by and sender.referred_by.commission_received == False:
                referral = sender.referred_by
                referred_by_user = sender.referred_by.user
                referred_by_maturity = referred_by_user.maturity
                user_ref_commision = referral.commission_earned
                if referred_by_maturity - referred_by_user.total_withdrawal >= referral_commission:
                    referred_by_user.total_withdrawal += referral_commission
                    referred_by_user.save()
                    referral.increase_commission_earned(referral_commission)
                    commission_transaction = Transaction.objects.create(
                        sender=sender,
                        amount=referral_commission,
                        crypto_name=crypto_name,
                        transaction_type='Referral'
                    )
                    referral.commission_transactions = commission_transaction
                    referral.user.total_withdrawal += referral_commission
                    referral.save()
                    serializer.save(amount = amount)
                    sender.maturity += amount*2
                    sender.referred_by.mark_commission_received()
                    sender.total_deposit += amount
                    sender.save()
                elif referred_by_maturity - referred_by_user.total_withdrawal < referral_commission and referred_by_maturity- referred_by_user.total_withdrawal != 0:
                    commision_added = referred_by_maturity - referred_by_user.total_withdrawal
                    referred_by_user.total_withdrawal += commision_added
                    referred_by_user.save()
                    referral.increase_commission_earned(commision_added)
                    commission_transaction = Transaction.objects.create(
                        # sender=referral.user,
                        sender=sender,
                        amount=commision_added,
                        crypto_name=crypto_name,
                        transaction_type='Referral'
                    )
                    referral.commission_transactions = commission_transaction

                    referral.save()
                    serializer.save(amount = amount)
                    sender.maturity += amount*2
                    sender.total_deposit += amount
                    sender.referred_by.mark_commission_received()
                    sender.save()
                
                else:
                    
                    sender.maturity += amount*2
                    sender.total_deposit += amount
                    sender.save()
                    serializer.save(amount = amount)

            else:
                sender.maturity += amount*2
                sender.total_deposit += amount
                sender.save()
                serializer.save(amount = amount)
        elif transaction_type == 'Transfer':
            serializer.save()
        elif transaction_type == 'Receiver':
            serializer.save()

        else:
            sender.total_withdrawal += amount
            sender.save()
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
        transactions = Transaction.objects.filter(sender=instance).exclude(transaction_type = 'Referral')
        serializer = self.get_serializer(transactions, many=True)

        total_deposit = transactions.filter(transaction_type='Deposit').aggregate(
            total_deposit=models.Sum('amount'))['total_deposit'] or 0
        total_withdrawal = transactions.filter(transaction_type='Withdrawal').aggregate(
            total_withdrawal=models.Sum('amount'))['total_withdrawal'] or 0
        referrals = Referral.objects.filter(user=instance)
        total_commission_earned = referrals.aggregate(total_commission=models.Sum('commission_earned'))['total_commission'] or 0
        
        
        response_data = {
            'total_deposit': total_deposit,
            'total_withdrawal': total_withdrawal+total_commission_earned,
            'transactions': serializer.data
        }
        return Response(response_data)
