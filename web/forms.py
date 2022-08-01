from __future__ import unicode_literals
from django import forms

from .models import Pick,Drop



class PickForm(forms.Form):
    number    = forms.IntegerField(required=True,   widget=forms.TextInput(attrs={'placeholder':'Order On', 'class':'form-control', 'id':'OrdrNumberInput' }))
    class Meta:
       model = Pick
class DropForm(forms.Form):
    number    = forms.IntegerField(required=True,   widget=forms.TextInput(attrs={'placeholder':'Order On', 'class':'form-control', 'id':'OrdrNumberInput' }))
    class Meta:
       model = Pick

class CodeForm(forms.Form):
    code    = forms.CharField(required=True,   widget=forms.TextInput(attrs={'placeholder':'Code No', 'class':'form-control', 'id':'CodeNumberInput' }))
    class Meta:
       model = Pick
       