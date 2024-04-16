from django.contrib import admin

from .models import AdminUser, AdminTransaction, ProfitUpdate, ProtocolFee, CommissionUpdate, MinimumDeposit, MinimumWithdraw, WalletToPool, TopAnnouncement, ManagerUser

admin.site.register(AdminUser)
admin.site.register(AdminTransaction)
admin.site.register(ProfitUpdate)
admin.site.register(ProtocolFee)
admin.site.register(CommissionUpdate)
admin.site.register(MinimumDeposit)
admin.site.register(MinimumWithdraw)
admin.site.register(WalletToPool)
admin.site.register(TopAnnouncement)
admin.site.register(ManagerUser)
