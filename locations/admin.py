from django.contrib import admin

from .models import Locality


@admin.register(Locality)
class LocalityAdmin(admin.ModelAdmin):
    list_display = ("name", "province", "municipality", "locality_type", "is_active", "sort_order")
    list_filter = ("province", "locality_type", "is_active")
    search_fields = ("name", "municipality", "province", "search_text", "slug")
    ordering = ("province", "sort_order", "name")
    prepopulated_fields = {"slug": ("name",)}
