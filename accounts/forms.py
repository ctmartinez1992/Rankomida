from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox, ReCaptchaV2Invisible

from .models import UserProfile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    captcha = ReCaptchaField(label="", widget=ReCaptchaV2Checkbox())

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class LoginForm(AuthenticationForm):
    captcha = ReCaptchaField(label="", widget=ReCaptchaV2Checkbox())


class ProfileVisibilityForm(forms.ModelForm):
    captcha = ReCaptchaField(label="", widget=ReCaptchaV2Invisible())

    class Meta:
        model = UserProfile
        fields = ["is_public"]
        labels = {"is_public": "Make my profile public"}
