from decimal import Decimal, InvalidOperation
from django import template

register = template.Library()


@register.filter
def uzs(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return value

    formatted = format(amount.quantize(Decimal("1")), ",") if amount == amount.to_integral_value() else format(amount.quantize(Decimal("0.01")), ",")
    return formatted.replace(",", ".")
