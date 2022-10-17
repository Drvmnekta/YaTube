"""Module with custom filters for templates."""

from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Add class to css tag."""
    return field.as_widget(attrs={'class': css})
