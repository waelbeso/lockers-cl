from __future__ import unicode_literals
from django import forms

#from .models import Pick,Drop



class OpenForm(forms.Form):
   cell = forms.CharField(widget=forms.HiddenInput())

class CodeForm(forms.Form):
    code    = forms.CharField(required=True,   widget=forms.TextInput(attrs={'placeholder':'Code No', 'class':'form-control', 'id':'CodeNumberInput' }))
       