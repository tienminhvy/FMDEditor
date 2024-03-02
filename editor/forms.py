from typing import Any
from django import forms
from django.contrib.auth import authenticate


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100, required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

class RegisterForm(forms.Form):
    username = forms.CharField(label="Username", max_length=100, required=True)
    email = forms.EmailField(label="Email", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput())
    c_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput())

    # validation
    def clean(self) -> dict[str, Any]:
        if self.cleaned_data['password'] != self.cleaned_data['c_password']:
            raise forms.ValidationError("Passwords don't match")
        return super().clean()