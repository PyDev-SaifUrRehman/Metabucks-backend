from django.core.exceptions import ObjectDoesNotExist
from rest_framework import mixins
from metabucksapp.models import Referral
from metabucksapp.serializers import ReferralSerializer
from metabucksapp.serializers import TransactionSerializer
from metabucksapp.models import Transaction
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from metabucksapp.utils import generate_invitation_code
from .models import AdminUser, AdminTransaction, BaseUser, ProfitUpdate, ProtocolFee, CommissionUpdate, MinimumDeposit, MinimumWithdraw, TopAnnouncement, ManagerUser
from .serializers import AdminSerializer, AdminTransactionSerializer, AdminReferralSerializer, ProfitUpdateSerializer, ProtocolFeeSerializer, CommissionUpdateSerializer, MinimumDepositSerializer, MinimumWithdrawSerializer, WalletToPoolSerializer, TopAnnouncementSerializer, ManagerSerializer, AdminManagerSerializer, GetAdminSerializer
from metabucksapp.models import ClientUser
from metabucksapp.serializers import ClientUserSerializer
from metabucksapp.utils import generate_invitation_code
from django.db.models import F

class AdminUserViewset(ModelViewSet):
    serializer_class = AdminSerializer

    def list(self, request, *args, **kwargs):

        wallet_address_from_cookie = self.request.query_params.get('address')
        if not wallet_address_from_cookie:
            return Response({"detail": "No wallet address"}, status=status.HTTP_403_FORBIDDEN)    
        if wallet_address_from_cookie:
            try:
                admin_user = AdminUser.objects.get(
                    wallet_address=wallet_address_from_cookie) or ManagerUser.objects.get(wallet_address=wallet_address_from_cookie)
            except AdminUser.DoesNotExist:
                try:
                    admin_user = ManagerUser.objects.get(wallet_address=wallet_address_from_cookie)
                except ManagerUser.DoesNotExist:
                    return Response({"detail": "You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        if admin_user.user_type not in ['Admin', 'Manager']:
            return Response({"detail": "You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        queryset = admin_user
        serializer = GetAdminSerializer(queryset, many=True)
        total_deposit = ClientUser.objects.all().aggregate(total_deposit = Sum("total_deposit"))['total_deposit'] or 0
        total_withdrawal = ClientUser.objects.all().aggregate(total_withdrawal = Sum("total_withdrawal"))['total_withdrawal'] or 0
        total_maturity = ClientUser.objects.all().aggregate(maturity = Sum("maturity"))["maturity"] or 0
        total_withdrawal = ClientUser.objects.all().aggregate(total_withdrawal = Sum("total_withdrawal"))["total_withdrawal"] or 0
        net_deposit = ClientUser.objects.exclude(total_withdrawal=F('maturity')).aggregate(total_deposit = Sum("total_deposit"))['total_deposit'] or 0
        net_maturity = ClientUser.objects.exclude(total_withdrawal=F('maturity')).aggregate(maturity = Sum("maturity"))["maturity"] or 0
        data = {
            'wallet_address': queryset.wallet_address,
            'user_type': queryset.user_type,
            'total_deposit': total_deposit  ,
            'total_withdrawal': total_withdrawal,
            'total_maturity': total_maturity,
            'net_deposit':net_deposit,
            'net_maturity':net_maturity
        }
        queryset.total_deposit = total_deposit 
        queryset.total_withdrawal = total_withdrawal 
        queryset.maturity = total_maturity
        queryset.save()
        return Response({"data": data}, status=status.HTTP_200_OK)


class TransactionsViewset(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = AdminTransactionSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['crypto_name','sender__wallet_address',
                        'sender__referred_by__user__wallet_address', 'transaction_type']
    
    def list(self, request, *args, **kwargs):
        wallet_address_from_cookie = self.request.query_params.get('address')
        if wallet_address_from_cookie is None:
            return Response({"detail": "No wallet address"}, status=status.HTTP_403_FORBIDDEN)
            
        if wallet_address_from_cookie:
            try:
                admin_user = AdminUser.objects.get(
                    wallet_address=wallet_address_from_cookie) or ManagerUser.objects.get(wallet_address=wallet_address_from_cookie)
            except AdminUser.DoesNotExist:
                try:
                    admin_user = ManagerUser.objects.get(wallet_address=wallet_address_from_cookie)
                except ManagerUser.DoesNotExist:
                    return Response({"detail": "You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        if admin_user.user_type not in ['Admin', 'Manager']:
            return Response({"detail": "You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)


class UserReferralsViewset(ModelViewSet):

    queryset = Transaction.objects.all()
    serializer_class = AdminReferralSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['transaction_type']

    def list(self, request, *args, **kwargs):
        wallet_address_from_cookie = self.request.query_params.get('address')
        if not wallet_address_from_cookie:
            return Response({"detail": "No wallet address"}, status=status.HTTP_403_FORBIDDEN)
            
        if wallet_address_from_cookie:
            try:
                admin_user = AdminUser.objects.get(
                    wallet_address=wallet_address_from_cookie) or ManagerUser.objects.get(wallet_address=wallet_address_from_cookie)
            except AdminUser.DoesNotExist:
                try:
                    admin_user = ManagerUser.objects.get(wallet_address=wallet_address_from_cookie)
                except ManagerUser.DoesNotExist:
                    return Response({"detail": "You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        if admin_user.user_type not in ['Admin', 'Manager']:
            return Response({"detail": "You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)

# setting related
class ProfitUpdateViewSet(viewsets.ViewSet):
    def list(self, request):
        profit_update, created = ProfitUpdate.objects.get_or_create(pk=1)
        serializer = ProfitUpdateSerializer(
            profit_update, context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        profit_update, created = ProfitUpdate.objects.get_or_create(pk=1)
        serializer = ProfitUpdateSerializer(
            profit_update, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProtocolFeeViewSet(viewsets.ViewSet):

    def update(self, request, pk=None):
        protocol_fee, created = ProtocolFee.objects.get_or_create(pk=1)
        serializer = ProtocolFeeSerializer(
            protocol_fee, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommissionUpdateViewSet(viewsets.ViewSet):

    def update(self, request, pk=None):
        commission_update, created = CommissionUpdate.objects.get_or_create(
            pk=1)
        serializer = CommissionUpdateSerializer(
            commission_update, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MinimumDepositViewSet(viewsets.ViewSet):

    def update(self, request, pk=None):
        minimum_deposit, created = MinimumDeposit.objects.get_or_create(pk=1)
        serializer = MinimumDepositSerializer(
            minimum_deposit, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MinimumWithdrawViewSet(viewsets.ViewSet):

    def update(self, request, pk=None):
        minimum_withdraw, created = MinimumWithdraw.objects.get_or_create(pk=1)
        serializer = MinimumWithdrawSerializer(
            minimum_withdraw, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WalletToPoolViewSet(viewsets.ViewSet):
    def create(self, request):

        serializer = WalletToPoolSerializer(
            data=request.data, context={'request': request})
        new_user_referral_code = generate_invitation_code()
        serializer.is_valid(raise_exception=True)
        wallet_address = serializer.validated_data.get('wallet_address')
        deposit_amount = serializer.validated_data.get('admin_added_deposit', 0)
        maturity_amount = serializer.validated_data.get('admin_maturity', 0)
        admin_added_withdrawal = serializer.validated_data.get('admin_added_withdrawal', 0)
        crypto_name = serializer.validated_data.get('crypto_name', 'USDT')
        serializer.save(total_deposit = deposit_amount, total_withdrawal = admin_added_withdrawal, maturity = maturity_amount, referral_code = new_user_referral_code)
        try:
            sender = ClientUser.objects.get(wallet_address = wallet_address)
            print("sender", sender)
            if deposit_amount:
                Transaction.objects.create(sender = sender, amount = deposit_amount, transaction_type = 'Deposit', crypto_name = crypto_name)
            if admin_added_withdrawal:
                Transaction.objects.create(sender = sender, amount = admin_added_withdrawal, transaction_type = 'Withdrawal', crypto_name = crypto_name)
        except:
            return Response({"message": "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
        serializer_data = serializer.data
        return Response(serializer_data, status=status.HTTP_201_CREATED)


class AdminManagerViewset(viewsets.ModelViewSet):
    queryset = ManagerUser.objects.all()
    serializer_class = ManagerSerializer
    lookup_field = 'wallet_address'

    def destroy(self, request, *args, **kwargs):
        wallet_address_from_cookie = self.request.query_params.get('address')
        if wallet_address_from_cookie is None:
            return Response({"detail": "No wallet address"}, status=status.HTTP_403_FORBIDDEN)
            
        if wallet_address_from_cookie:
            try:
                admin_user = AdminUser.objects.get(
                    wallet_address=wallet_address_from_cookie)
            except AdminUser.DoesNotExist:
                
                return Response({"detail": "You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)

        if admin_user.user_type not in ['Admin']:
            return Response({"detail": "You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"msg":"Manager Deleted"}, status=status.HTTP_204_NO_CONTENT)


class TopAnnouncementViewSet(viewsets.ModelViewSet):
    queryset = TopAnnouncement.objects.all()
    serializer_class = TopAnnouncementSerializer


class AdminAndManagerListViewset(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = AdminManagerSerializer

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        admin_list = AdminUser.objects.all().values('wallet_address')
        manager_list = ManagerUser.objects.all().values('wallet_address')
        return Response({"admins": admin_list, "managers": manager_list}, status=status.HTTP_200_OK)


class CreateClientUserViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = ClientUser.objects.all()
    serializer_class = ClientUserSerializer

    def create(self, request):
        wallet_address_from_cookie = self.request.query_params.get('address')
        if wallet_address_from_cookie is None:
            return Response({"detail": "No wallet address"}, status=status.HTTP_403_FORBIDDEN)
       
        if wallet_address_from_cookie:
            try:
                admin_user = AdminUser.objects.get(
                    wallet_address=wallet_address_from_cookie)
            except AdminUser.DoesNotExist:
                return Response({"detail": "You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        if admin_user.user_type not in ['Admin']:
            return Response({"detail": "You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        
        new_user_referral_code = generate_invitation_code()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(referral_code=new_user_referral_code)
        user.save()
        serializer_data = serializer.data
        return Response(serializer_data, status=status.HTTP_201_CREATED)

class GetSettingAttributesViewset(viewsets.GenericViewSet, mixins.ListModelMixin):

    def list(self, request, *args, **kwargs):
        data = {}

        try:
            minimum_withdraw = MinimumWithdraw.objects.get(pk=1).amount
        except ObjectDoesNotExist:
            minimum_withdraw = 50.0

        try:
            minimum_deposit = MinimumDeposit.objects.get(pk=1).amount
        except ObjectDoesNotExist:
            minimum_deposit = 50.0

        try:
            protocol_fee = ProtocolFee.objects.get(pk=1)
            deposit_fee = protocol_fee.deposit_fee
            withdraw_fee = protocol_fee.withdraw_fee
        except ObjectDoesNotExist:
            deposit_fee = 5.0
            withdraw_fee = 5.0

        data['minimum_withdraw'] = minimum_withdraw
        data['minimum_deposit'] = minimum_deposit
        data['deposit_fee'] = deposit_fee
        data['withdraw_fee'] = withdraw_fee

        return Response(data, status=status.HTTP_200_OK)

