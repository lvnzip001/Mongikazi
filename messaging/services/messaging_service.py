from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from messaging.models import Message, MessageThread


def _is_thread_participant(thread, user):
    return bool(user and user.id in [thread.employer_user_id, thread.helper_user_id])


def _assert_thread_participant(thread, user):
    if not _is_thread_participant(thread, user):
        raise ValidationError("You do not have access to this thread.")


def _assert_booking_thread_allowed(booking):
    if not booking.worker_id:
        raise ValidationError("Messaging becomes available once a helper is assigned to the booking.")


def _resolve_participants_from_booking(booking):
    return booking.employer.user, booking.worker.user


@transaction.atomic
def open_or_get_thread_for_booking(*, booking, actor):
    _assert_booking_thread_allowed(booking)
    employer_user, helper_user = _resolve_participants_from_booking(booking)
    if actor.id not in [employer_user.id, helper_user.id]:
        raise ValidationError("Only booking participants can open this chat.")

    thread, _created = MessageThread.objects.get_or_create(
        booking=booking,
        employer_user=employer_user,
        helper_user=helper_user,
        defaults={"status": MessageThread.Status.ACTIVE},
    )
    if thread.status != MessageThread.Status.ACTIVE:
        thread.status = MessageThread.Status.ACTIVE
        thread.save(update_fields=["status", "updated_at"])
    return thread


@transaction.atomic
def send_message(*, thread, sender, body):
    _assert_thread_participant(thread, sender)
    if thread.status != MessageThread.Status.ACTIVE:
        raise ValidationError("This thread is not active for new messages.")

    message = Message.objects.create(
        thread=thread,
        sender=sender,
        body=(body or "").strip(),
    )
    thread.last_message_at = message.created_at
    thread.save(update_fields=["last_message_at", "updated_at"])
    return message


@transaction.atomic
def mark_thread_read(*, thread, reader):
    _assert_thread_participant(thread, reader)
    now = timezone.now()

    if reader.id == thread.employer_user_id:
        Message.objects.filter(thread=thread, read_by_employer_at__isnull=True).exclude(sender=reader).update(read_by_employer_at=now)
        return

    Message.objects.filter(thread=thread, read_by_helper_at__isnull=True).exclude(sender=reader).update(read_by_helper_at=now)


@transaction.atomic
def archive_thread(*, thread, actor):
    _assert_thread_participant(thread, actor)
    thread.status = MessageThread.Status.ARCHIVED
    thread.save(update_fields=["status", "updated_at"])
    return thread

