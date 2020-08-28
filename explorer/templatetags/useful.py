from django import template
from django.conf import settings

register = template.Library()

HOME_MENU_ITEM = 'home'
LOGS_MENU_ITEM = 'logs'
NEW_MENU_ITEM = 'new_query'
PLAY_MENU_ITEM = 'playground'
TABLE_BROWSER_MENU_ITEM = 'table_browser'


@register.simple_tag
def is_table_browser_enabled():
    return settings.ENABLE_TABLE_BROWSER


@register.simple_tag(takes_context=True)
def get_active_menu(context):
    view_name = context['request'].resolver_match.url_name
    if view_name in ['explorer_index', 'query_detail']:
        return HOME_MENU_ITEM
    if view_name == 'explorer_logs':
        return LOGS_MENU_ITEM
    if view_name == 'explorer_playground':
        return PLAY_MENU_ITEM
    if view_name == 'query_create':
        return NEW_MENU_ITEM
    if view_name in ['connection_browser_list', 'table_browser_list', 'table_browser_detail']:
        return TABLE_BROWSER_MENU_ITEM
