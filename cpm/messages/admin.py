__author__ = 'wpl'

from django.contrib import admin
from .models import Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1

admin.site.register(Message)