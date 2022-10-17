"""Module with views of About app."""

from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """View of About author page."""

    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """View of About tech page."""
    
    template_name = 'about/tech.html'
