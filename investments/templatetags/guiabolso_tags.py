from django import template
from django.utils.safestring import mark_safe
import wcag_contrast_ratio as contrast

register = template.Library()

@register.filter
def color(transaction, categories):
	if transaction.category in categories:
		return categories[transaction.category].color
	return 'eeeeee'

@register.filter
def text_color(transaction, categories):
	if transaction.category not in categories:
		return '000000'

	color = categories[transaction.category].color
	rgb = tuple(int(color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
	white = (1.0, 1.0, 1.0)
	black = (0.0, 0.0, 0.0)

	if contrast.rgb(rgb, white) > contrast.rgb(rgb, black):
		return "FFFFFF"
	else:
		return "000000"

@register.filter(is_safe=True)
def symbol(transaction, categories):
	if transaction.category in categories:
		category = categories[transaction.category]
		if category.symbol is not None:
			return mark_safe(f"<i class='mr-1 {category.symbol}'></i>")
	return ''