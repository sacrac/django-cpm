__author__ = 'wpl'

from django.contrib import admin
from .models import Project, ProjectImage
from tasks.admin import TaskInline
from updates.admin import UpdateInline
from changes.admin import ChangeOrderInline


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


class ProjectAdmin(admin.ModelAdmin):
    inlines = [TaskInline, UpdateInline, ChangeOrderInline, ProjectImageInline]

admin.site.register(Project, ProjectAdmin)