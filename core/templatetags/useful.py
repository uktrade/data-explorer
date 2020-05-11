from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def is_table_browser_enabled():
    return settings.ENABLE_TABLE_BROWSER

