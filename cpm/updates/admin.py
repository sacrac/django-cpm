__author__ = 'wpl'

from django.contrib import admin
from .models import Update


class UpdateInline(admin.TabularInline):
    model = Update
    extra = 1

admin.site.register(Update)