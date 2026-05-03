from django.contrib import admin
from .models import MeritData


@admin.register(MeritData)
class MeritDataAdmin(admin.ModelAdmin):
    list_display = ('program', 'faculty', 'merit_percentage', 'campus', 'year')
    list_filter = ('faculty', 'campus', 'year', 'semester')
    search_fields = ('program', 'faculty')
    ordering = ('-year', 'faculty')
