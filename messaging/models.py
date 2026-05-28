from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class MessageThread(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ARCHIVED = "ARCHIVED", "Archived"
        CLOSED = "CLOSED", "Closed"

    booking = models.ForeignKey(
        "bookings.Booking",
        on_delete=models.CASCADE,
        related_name="message_threads",
        null=True,
        blank=True,
    )
    employer_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employer_message_threads",
    )
    helper_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="helper_message_threads",
    )
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    last_message_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_message_at", "-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["booking", "employer_user", "helper_user"],
                name="unique_thread_for_booking_participants",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "last_message_at"]),
            models.Index(fields=["employer_user", "status"]),
            models.Index(fields=["helper_user", "status"]),
        ]

    def clean(self):
        if self.employer_user_id and not self.employer_user.is_employer:
            raise ValidationError({"employer_user": "Employer participant must have EMPLOYER role."})
        if self.helper_user_id and not self.helper_user.is_helper:
            raise ValidationError({"helper_user": "Helper participant must have HELPER role."})

        if self.booking_id:
            if not self.booking.worker_id:
                raise ValidationError({"booking": "Cannot start a message thread before a worker is assigned."})
            if self.booking.employer.user_id != self.employer_user_id:
                raise ValidationError({"employer_user": "Employer participant does not match booking employer."})
            if self.booking.worker.user_id != self.helper_user_id:
                raise ValidationError({"helper_user": "Helper participant does not match booking worker."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        booking_ref = self.booking.booking_reference if self.booking else "direct"
        return f"Thread {self.pk} ({booking_ref})"


class Message(models.Model):
    class MessageType(models.TextChoices):
        TEXT = "TEXT", "Text"

    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    body = models.TextField(max_length=2000)
    message_type = models.CharField(max_length=12, choices=MessageType.choices, default=MessageType.TEXT)
    is_system = models.BooleanField(default=False)
    read_by_employer_at = models.DateTimeField(null=True, blank=True)
    read_by_helper_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["created_at", "id"]
        indexes = [
            models.Index(fields=["thread", "created_at"]),
            models.Index(fields=["sender", "created_at"]),
        ]

    def clean(self):
        if self.sender_id not in [self.thread.employer_user_id, self.thread.helper_user_id]:
            raise ValidationError({"sender": "Sender must be a participant in this thread."})
        if not (self.body or "").strip() and not self.is_system:
            raise ValidationError({"body": "Message body cannot be blank."})

    def save(self, *args, **kwargs):
        self.body = (self.body or "").strip()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message {self.pk} in thread {self.thread_id}"

