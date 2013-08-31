__author__ = 'wpl'

from django.contrib import admin
from .models import ChangeOrder


class ChangeOrderInline(admin.TabularInline):
    model = ChangeOrder
    extra = 1

admin.site.register(ChangeOrder)