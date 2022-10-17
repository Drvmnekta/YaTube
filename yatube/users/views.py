"""Module with views of users app."""

from django.urls import reverse_lazy
from django.views.generic import CreateView

from yatube.users.forms import CreationForm


class SignUp(CreateView):
    """View of user creation."""
    
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'
