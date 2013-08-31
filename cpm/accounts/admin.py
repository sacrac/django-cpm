__author__ = 'wpl'

from django.contrib import admin
from .models import Client, Company, Note, IPAddress, Visit

from django.contrib.auth.models import User

class VisitInline(admin.TabularInline):
    model = Visit
    extra = 1

class ClientInline(admin.TabularInline):
    model = Client

class NoteInline(admin.TabularInline):
    model = Note
    extra = 1

class IPAddressInline(admin.TabularInline):
    model = IPAddress
    extra = 1

class IPAddressAdmin(admin.ModelAdmin):
    inlines = [VisitInline]

class UserAdmin(admin.ModelAdmin):
    inlines = [ClientInline, NoteInline]


admin.site.register(Company)
admin.site.register(IPAddress, IPAddressAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)