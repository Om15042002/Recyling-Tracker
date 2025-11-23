from django import template

register = template.Library()

@register.filter
def mul(value, multiplier):
    """Multiply a value by the given multiplier."""
    try:
        return float(value) * float(multiplier)
    except (ValueError, TypeError):
        return 0

@register.filter
def subtract(value, subtrahend):
    """Subtract a value from another."""
    try:
        return float(value) - float(subtrahend)
    except (ValueError, TypeError):
        return 0