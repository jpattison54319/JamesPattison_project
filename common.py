"""Tiny shared helpers."""

import hashlib


def sha1_id(*parts) -> str:
    """Builds a stable id from whatever fields matter. Returns the SHA-1 hex string."""
    joined = "|".join("" if p is None else str(p) for p in parts)
    return hashlib.sha1(joined.encode("utf-8")).hexdigest()


def short_metric(type_str: str) -> str:
    """Drops the long HealthKit prefix when there is one. Returns the shorter metric name."""
    for prefix in (
        "HKQuantityTypeIdentifier",
        "HKCategoryTypeIdentifier",
        "HKDataType",
        "HKWorkoutActivityType",
    ):
        if type_str.startswith(prefix):
            return type_str[len(prefix) :]
    return type_str


def to_float(value):
    """Turns a value into a float and treats blanks or bad values as missing. Returns a float, or None."""
    if value is None:
        return None
    value = value.strip() if isinstance(value, str) else value
    if value == "" or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def to_int(value):
    """Turns a value into an integer through the float helper. Returns an int, or None for missing or invalid input."""
    f = to_float(value)
    return None if f is None else int(f)
