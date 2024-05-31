from django import forms

class MyForm(forms.Form):
    field1 = forms.CharField(label='Field 1', max_length=100)
    field2 = forms.CharField(label='Field 2', max_length=100)