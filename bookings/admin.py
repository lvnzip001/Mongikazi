from django.contrib import admin

from bookings.models import Booking, BookingEvent


class BookingEventInline(admin.TabularInline):
    model = BookingEvent
    extra = 0
    fields = ("event_type", "from_status", "to_status", "description", "performed_by", "created_at")
    readonly_fields = ("event_type", "from_status", "to_status", "description", "performed_by", "created_at")
    can_delete = False


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "booking_reference",
        "status",
        "employer",
        "worker",
        "service_category",
        "scheduled_date",
        "start_time",
        "total_estimate",
    )
    list_filter = ("status", "scheduled_date", "service_category")
    search_fields = (
        "booking_reference",
        "employer__display_name",
        "worker__display_name",
        "employer__user__email",
        "worker__user__email",
    )
    readonly_fields = ("booking_reference", "created_at", "updated_at", "completed_at")
    inlines = [BookingEventInline]


@admin.register(BookingEvent)
class BookingEventAdmin(admin.ModelAdmin):
    list_display = ("booking", "event_type", "from_status", "to_status", "performed_by", "created_at")
    list_filter = ("event_type", "to_status")
    search_fields = ("booking__booking_reference", "description")
    readonly_fields = ("created_at",)
