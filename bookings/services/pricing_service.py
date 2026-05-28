from decimal import Decimal, ROUND_HALF_UP


HOURLY_WORKER_RATE = Decimal("75.00")
PLATFORM_FEE_RATE = Decimal("0.15")


def estimate_booking_price(service_category, duration_hours):
    """Return transparent booking estimates for worker, platform, and total fees."""
    del service_category  # Pricing per category can be introduced in a later phase.

    hours = Decimal(duration_hours)
    worker_fee = (HOURLY_WORKER_RATE * hours).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    platform_fee = (worker_fee * PLATFORM_FEE_RATE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = (worker_fee + platform_fee).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "worker_fee_estimate": worker_fee,
        "platform_fee_estimate": platform_fee,
        "total_estimate": total,
    }
