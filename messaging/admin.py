from django.contrib import admin

from messaging.models import Message, MessageThread


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ("sender", "body", "created_at")
    readonly_fields = ("created_at",)


@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "employer_user", "helper_user", "status", "last_message_at", "updated_at")
    list_filter = ("status",)
    search_fields = ("booking__booking_reference", "employer_user__email", "helper_user__email")
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "thread", "sender", "created_at")
    search_fields = ("thread__booking__booking_reference", "sender__email", "body")
    list_select_related = ("thread", "sender")

