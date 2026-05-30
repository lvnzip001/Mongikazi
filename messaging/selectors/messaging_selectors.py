from django.db.models import Count, Q

from messaging.models import Message, MessageThread


def get_thread_for_user(thread_id, user):
    return (
        MessageThread.objects.select_related("booking", "employer_user", "helper_user")
        .filter(Q(employer_user=user) | Q(helper_user=user), id=thread_id)
        .first()
    )


def get_thread_for_booking_and_user(booking, user):
    return (
        MessageThread.objects.select_related("booking", "employer_user", "helper_user")
        .filter(booking=booking)
        .filter(Q(employer_user=user) | Q(helper_user=user))
        .first()
    )


def get_threads_for_employer(user):
    return (
        MessageThread.objects.select_related("booking", "helper_user")
        .filter(employer_user=user)
        .annotate(
            unread_count=Count(
                "messages",
                filter=Q(messages__read_by_employer_at__isnull=True) & ~Q(messages__sender=user),
            )
        )
    )


def get_threads_for_helper(user):
    return (
        MessageThread.objects.select_related("booking", "employer_user")
        .filter(helper_user=user)
        .annotate(
            unread_count=Count(
                "messages",
                filter=Q(messages__read_by_helper_at__isnull=True) & ~Q(messages__sender=user),
            )
        )
    )


def get_thread_messages(thread, limit=120):
    return Message.objects.select_related("sender").filter(thread=thread).order_by("created_at", "id")[:limit]


def get_unread_counts_for_user(user):
    if getattr(user, "is_employer", False):
        total_unread = Message.objects.filter(thread__employer_user=user, read_by_employer_at__isnull=True).exclude(sender=user).count()
        thread_count = (
            MessageThread.objects.filter(employer_user=user)
            .annotate(unread_count=Count("messages", filter=Q(messages__read_by_employer_at__isnull=True) & ~Q(messages__sender=user)))
            .filter(unread_count__gt=0)
            .count()
        )
        return {"threads_with_unread": thread_count, "total_unread": total_unread}

    if getattr(user, "is_helper", False):
        total_unread = Message.objects.filter(thread__helper_user=user, read_by_helper_at__isnull=True).exclude(sender=user).count()
        thread_count = (
            MessageThread.objects.filter(helper_user=user)
            .annotate(unread_count=Count("messages", filter=Q(messages__read_by_helper_at__isnull=True) & ~Q(messages__sender=user)))
            .filter(unread_count__gt=0)
            .count()
        )
        return {"threads_with_unread": thread_count, "total_unread": total_unread}

    return {"threads_with_unread": 0, "total_unread": 0}


def get_booking_thread_unread_count(booking, user):
    return get_booking_unread_counts_map([booking], user).get(booking.id, 0)


def get_booking_unread_counts_map(bookings, user):
    """Return booking.id -> unread count for the given user (batched)."""
    booking_list = list(bookings)
    if not booking_list:
        return {}

    booking_ids = [booking.id for booking in booking_list]
    counts = dict.fromkeys(booking_ids, 0)

    if getattr(user, "is_employer", False):
        threads = MessageThread.objects.filter(booking_id__in=booking_ids, employer_user=user).annotate(
            unread_count=Count(
                "messages",
                filter=Q(messages__read_by_employer_at__isnull=True) & ~Q(messages__sender=user),
            )
        )
    elif getattr(user, "is_helper", False):
        threads = MessageThread.objects.filter(booking_id__in=booking_ids, helper_user=user).annotate(
            unread_count=Count(
                "messages",
                filter=Q(messages__read_by_helper_at__isnull=True) & ~Q(messages__sender=user),
            )
        )
    else:
        return counts

    for thread in threads:
        if thread.booking_id:
            counts[thread.booking_id] = thread.unread_count
    return counts


def get_recent_unread_threads_for_user(user, limit=2):
    if getattr(user, "is_employer", False):
        return list(get_threads_for_employer(user).filter(unread_count__gt=0).order_by("-last_message_at")[:limit])
    if getattr(user, "is_helper", False):
        return list(get_threads_for_helper(user).filter(unread_count__gt=0).order_by("-last_message_at")[:limit])
    return []

