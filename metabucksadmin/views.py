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

from .models import AdminUser, AdminTransaction, BaseUser, ProfitUpdate, ProtocolFee, CommissionUpdate, MinimumDeposit, MinimumWithdraw, WalletToPool, TopAnnouncement, ManagerUser
from .serializers import AdminSerializer, AdminTransactionSerializer, AdminReferralSerializer, ProfitUpdateSerializer, ProtocolFeeSerializer, CommissionUpdateSerializer, MinimumDepositSerializer, MinimumWithdrawSerializer, WalletToPoolSerializer, TopAnnouncementSerializer, ManagerSerializer, AdminManagerSerializer, GetAdminSerializer
from metabucksapp.models import ClientUser
from metabucksapp.serializers import ClientUserSerializer
from metabucksapp.utils import generate_invitation_code


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
                print("admin", admin_user)
            except AdminUser.DoesNotExist:
                try:
                    admin_user = ManagerUser.objects.get(wallet_address=wallet_address_from_cookie)
                except ManagerUser.DoesNotExist:
                    return Response({"detail": "You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        if admin_user.user_type not in ['Admin', 'Manager']:
            return Response({"detail": "You don't have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        queryset = admin_user
        serializer = GetAdminSerializer(queryset, many=True)
        total_deposit = Transaction.objects.filter(transaction_type = 'Deposit').aggregate(depo = Sum("amount"))["depo"] or 0
        total_withdrawal = Transaction.objects.filter(transaction_type = 'Withdrawal').aggregate(withdraw = Sum("amount"))["withdraw"] or 0
        total_maturity = ClientUser.objects.all().aggregate(maturity = Sum("maturity"))["maturity"] or 0
        data = {
            'wallet_address': queryset.wallet_address,
            'user_type': queryset.user_type,
            'total_deposit': total_deposit ,
            'total_withdrawal': total_withdrawal,
            'total_maturity': total_deposit*2,
        }
        queryset.total_deposit = total_deposit
        queryset.total_withdrawal = total_withdrawal
        queryset.maturity = total_deposit*2
        queryset.save()

        return Response({"data": data}, status=status.HTTP_200_OK)


class TransactionsViewset(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = AdminTransactionSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_fields = ['crypto_name',
                        'sender__wallet_address', 'transaction_type']
    
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
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class CreateClientUserViewSet(viewsets.ModelViewSet):
    queryset = ClientUser.objects.all()
    serializer_class = ClientUserSerializer

    def create(self, request):
    
        new_user_referral_code = generate_invitation_code()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(referral_code=new_user_referral_code)
        user.save()
        serializer_data = serializer.data
        return Response(serializer_data, status=status.HTTP_201_CREATED)
