"""Form definitions used by the locker web application."""

from __future__ import annotations

from django import forms


class OpenForm(forms.Form):
    """Hidden field that stores the locker identifier to open."""

    cell = forms.CharField(widget=forms.HiddenInput())


class CodeForm(forms.Form):
    """Form that accepts the access code provided to the customer."""

    code = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Code No",
                "class": "form-control",
                "id": "CodeNumberInput",
            }
        ),
    )
