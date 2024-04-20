from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'my-custom-class'}))
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
