from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import ContactForm, AdminForm, kenchiccnew

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]
class CreateAdminForm(forms.ModelForm):
    class Meta:
        model = AdminForm
        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]

# class DownloadForm(forms.Form):
#     url = forms.CharField(widget=forms.TextInput(attrs={ 'placeholder': 'Enter video url' }), label=False)


class FormPendingForm(forms.ModelForm):
    class Meta:
        model= ContactForm
        fields= ["shop_name", "invoicepicture"]


class FormContactForm(forms.ModelForm):
    class Meta:
        model= ContactForm
        fields= ["shop_name", "completion_status", "message" , "invoicepicture"]

class DeliveryForm(forms.ModelForm):
    class Meta:
        model = kenchiccnew
        fields= ["Customer_Name", "Posting_Description", "Route_Plan", "Ordered_Weight"]


