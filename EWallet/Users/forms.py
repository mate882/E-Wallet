from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class EmailBasedPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        active_users = User._default_manager.filter(email__iexact=email, is_active=True)
        return (u for u in active_users if u.has_usable_password())

