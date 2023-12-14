from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import validate_email
from validate_email import validate_email
from .models import Receipt
#Inherits from UserCreationForm, which is a built-in form in Django for user creation.
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse e-mail", validators=[validate_email])
    password1 = forms.CharField(
        label="Mot de passe",
        strip=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput,
        strip=False,
    )
    is_approved = forms.BooleanField(required=False, label="Approuvé")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "is_approved")

from django.forms.widgets import DateInput

#create a form for receipt's information
class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ['store_name', 'date_of_purchase', 'item_list', 'total_amount']
        widgets = {
            'date_of_purchase': DateInput(attrs={'type': 'date'}),
        }
