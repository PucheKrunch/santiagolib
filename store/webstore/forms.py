from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User

from .models import *

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','password1','password2']

class addClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['publisher']

class addProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','price','description','image','author','publisher','quantity','genre']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shiping','paying','address','quantity']