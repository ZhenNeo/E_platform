from django import forms
from .models import *
from django.utils import timezone


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=255, widget=forms.TextInput(
        attrs={'placeholder': 'Email'}))
    password = forms.CharField(max_length=255, widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}))

class UserForm(forms.ModelForm):
    class Meta:
        models = CustomeUser
        fields = ['username', 'email', 'password', 'user_type']  # Add or remove fields as needed

        labels = {
            'username': 'Username',
            'email': 'Email',
            'password': 'Password',
            'user_type': 'User Type',
        }
        widgets = {
            'password': forms.PasswordInput(),
        }

class AdminForm(forms.ModelForm):
    password1 = forms.CharField(max_length=255, widget=forms.PasswordInput(
        attrs={'placeholder': 'Create Password'}))
    password2 = forms.CharField(max_length=255, widget=forms.PasswordInput(
        attrs={'placeholder': 'Re-enter Password'}))
    DOB = forms.DateField(widget=forms.DateInput(
        attrs={'type': 'date'}))  # Ensure proper widget for DOB FIELD

    class Meta:
        model = Student
        fields = ['Full_Name', 'Mobile_no', 'EmailID',
                  'DOB', 'Gender', 'password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2