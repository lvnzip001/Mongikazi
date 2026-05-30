from messaging.selectors.messaging_selectors import get_unread_counts_for_user


def messaging_unread(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"messaging_unread": {"total_unread": 0, "threads_with_unread": 0}}
    if not (getattr(user, "is_employer", False) or getattr(user, "is_helper", False)):
        return {"messaging_unread": {"total_unread": 0, "threads_with_unread": 0}}
    return {"messaging_unread": get_unread_counts_for_user(user)}
