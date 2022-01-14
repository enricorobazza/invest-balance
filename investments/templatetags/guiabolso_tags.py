from django import template
from django.utils.safestring import mark_safe
import wcag_contrast_ratio as contrast

register = template.Library()

@register.filter
def text_color(transaction):
	color = transaction.category.color
	rgb = tuple(int(color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
	white = (1.0, 1.0, 1.0)
	black = (0.0, 0.0, 0.0)

	if contrast.rgb(rgb, white) > contrast.rgb(rgb, black):
		return "FFFFFF"
	else:
		return "000000"

@register.filter(is_safe=True)
def symbol(transaction):
	if transaction.category.symbol is not None:
		return mark_safe(f"<i class='mr-1 {transaction.category.symbol}'></i>")
	return ''