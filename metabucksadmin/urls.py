from rest_framework.routers import DefaultRouter
from .views import AdminUserViewset, TransactionsViewset, UserReferralsViewset, ProfitUpdateViewSet, ProtocolFeeViewSet, CommissionUpdateViewSet, MinimumDepositViewSet, MinimumWithdrawViewSet, WalletToPoolViewSet, TopAnnouncementViewSet, AdminManagerViewset, AdminAndManagerListViewset, CreateClientUserViewSet, GetSettingAttributesViewset

router = DefaultRouter()

router.register(r'user-signup', AdminUserViewset, basename='user')
router.register(r'transactions', TransactionsViewset, basename='trx')
router.register(r'referrals', UserReferralsViewset, basename='ref')

# setting
router.register(r'profit-update', ProfitUpdateViewSet,
                basename='profit-update')
router.register(r'protocol-fee', ProtocolFeeViewSet, basename='protocol-fee')
router.register(r'commission-update', CommissionUpdateViewSet,
                basename='commission-update')
router.register(r'minimum-deposit', MinimumDepositViewSet,
                basename='minimum-deposit')
router.register(r'minimum-withdraw', MinimumWithdrawViewSet,
                basename='minimum-withdraw')
router.register(r'add-wallet-to-pool', WalletToPoolViewSet,
                basename='add-wallet-to-pool')
router.register(r'top-announcement', TopAnnouncementViewSet,
                basename='top-announcement')

router.register(r'manager', AdminManagerViewset,
                basename='manager')
router.register(r'admin-manager', AdminAndManagerListViewset,
                basename='admin-manager')
router.register(r'create-client', CreateClientUserViewSet, basename='create-client')
router.register(r'setting-attrs', GetSettingAttributesViewset, basename='attrs')

urlpatterns = router.urls
