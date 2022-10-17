"""Module with core views of the project."""

from django.http import HttpResponse
from django.shortcuts import render


def page_not_found(request, exception) -> HttpResponse:
    """Render NotFound page."""
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason='') -> HttpResponse:
    """Render CSRF-failure page."""
    return render(request, 'core/403csrf.html')


def server_error(request) -> HttpResponse:
    """Render ServerError page."""
    return render(request, 'core/500.html', status=500)


def permission_denied_view(request, exception) -> HttpResponse:
    """Render PermissionDenied page."""
    return render(request, 'core/403.html', status=403)
