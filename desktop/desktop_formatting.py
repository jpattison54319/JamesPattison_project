"""Formatting and display semantics for the desktop views."""

from __future__ import annotations

from datetime import date
import os

from desktop.desktop_theme import COLORS


def format_number(value, digits: int = 0, suffix: str = "") -> str:
    """Formats a number for the desktop cards. Returns the formatted string, or an em dash when missing."""
    if value is None:
        return "—"
    return f"{value:,.{digits}f}{suffix}"


def format_minutes(value) -> str:
    """Formats minutes as minutes or hours so the cards stay compact. Returns the display string."""
    if value is None:
        return "—"
    minutes = float(value)
    if minutes >= 90:
        return f"{minutes / 60:.1f}h"
    return f"{minutes:.0f}m"


def format_date(value: str | None) -> str:
    """Formats an ISO date for the desktop UI. Returns a friendly date string, or the short raw value when parsing fails."""
    if not value:
        return "—"
    try:
        parsed = date.fromisoformat(value[:10])
    except ValueError:
        return value[:10]
    return f"{parsed:%b} {parsed.day}, {parsed:%Y}"


def format_volume(value) -> str:
    """Formats a lifting volume value with pounds. Returns the display string, or an em dash when missing."""
    if value is None:
        return "—"
    return f"{float(value):,.0f} lb"


def trend_style(change, lower_is_better: bool = False) -> tuple[str, str]:
    """Picks a direction marker and color for a month-over-month change. Returns the marker and color as a tuple."""
    if change is None or abs(change) < 0.5:
        return "→", COLORS["muted"]

    increased = change > 0
    favorable = not increased if lower_is_better else increased
    color = COLORS["green"] if favorable else COLORS["red"]
    return ("↑" if increased else "↓"), color


def format_percent_change(current, previous) -> str:
    """Formats the percent change between two values. Returns the display string, or an em dash when it cannot be calculated."""
    if current is None or previous in (None, 0):
        return "—"
    change = (current - previous) / previous * 100.0
    sign = "+" if change >= 0 else ""
    return f"{sign}{change:.1f}%"


def format_change_style(
    current,
    previous,
    lower_is_better: bool = False,
) -> tuple[str, str]:
    """Formats a change and picks its matching color. Returns the change string and color as a tuple."""
    if current is None or previous in (None, 0):
        return "—", COLORS["muted"]
    change = (current - previous) / previous * 100.0
    return (
        format_percent_change(current, previous),
        trend_style(
            change,
            lower_is_better=lower_is_better,
        )[1],
    )


def readiness_colors(readiness: str) -> tuple[str, str]:
    """Picks the foreground and background colors for a readiness state. Returns the two colors as a tuple."""
    return {
        "green": (COLORS["green"], COLORS["green_dark"]),
        "yellow": (COLORS["yellow"], COLORS["yellow_dark"]),
        "red": (COLORS["red"], COLORS["red_dark"]),
    }.get(readiness, (COLORS["accent"], COLORS["accent_dark"]))


def detect_local_timezone() -> str:
    """Uses the Mac/Linux timezone link when it is available. Returns the timezone name, with New York as the fallback."""
    try:
        location = os.path.realpath("/etc/localtime")
        if "zoneinfo/" in location:
            return location.split("zoneinfo/")[-1]
    except OSError:
        pass
    return "America/New_York"
