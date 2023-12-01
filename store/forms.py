from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from . import models


# Create your forms here.

class newUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password2']

    def save(self, commit=True):
        user = super(newUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class NewCustomerForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = (
            "kind",
        )


class NewHomeForm(forms.ModelForm):
    class Meta:
        model = models.Home
        fields = (
            "marriage_status",
            "gender",
            "age",
            "income"
        )


class NewBusinessForm(forms.ModelForm):
    class Meta:
        model = models.Business
        fields = (
            "business_category",
            "gross_annual_income"
        )
