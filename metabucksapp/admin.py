from django.contrib import admin
from .models import BaseUser, Referral, Transaction, ClientUser

admin.site.register(BaseUser)
admin.site.register(ClientUser)
admin.site.register(Referral)
admin.site.register(Transaction)
