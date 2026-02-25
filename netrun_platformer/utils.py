from __future__ import annotations


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(value, high))


def fmt_time(seconds: float) -> str:
    total = max(0, int(seconds))
    return f"{total // 60:02d}:{total % 60:02d}"

