from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from django.forms import ModelForm
from .models import *

class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username','email','password1','password2']

class ReviewForm(ModelForm):
	class Meta:
		model = Review
		fields = ['content','product','customer']

class ShippingAddressForm(ModelForm):
	class Meta:
		model = ShippingAddress
		exclude = ['date_created','id']