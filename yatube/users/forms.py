"""Module with forms for users app."""

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    """Form for user creation."""

    class Meta(UserCreationForm.Meta):
        """Meta-class of form for user creation."""
        
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
