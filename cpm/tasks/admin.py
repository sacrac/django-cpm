__author__ = 'wpl'

from django.contrib import admin
from .models import Task, TaskCategory, CategoryBundle


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1

admin.site.register(Task)
admin.site.register(TaskCategory)
admin.site.register(CategoryBundle)
