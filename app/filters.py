import django_filters
from django_filters import CharFilter,NumberFilter,ChoiceFilter
from django import forms
from .models import *


class ColorFilter(django_filters.FilterSet):
	
	product_name = CharFilter(field_name="product__name", lookup_expr="icontains")
	min_price = NumberFilter(field_name="product__final_price" ,lookup_expr="gte")
	max_price = NumberFilter(field_name="product__final_price", lookup_expr="lte")
	gender = ChoiceFilter(field_name="product__tags__name",choices= (("man","man"),("woman","woman")))
	brand = ChoiceFilter(field_name="product__tags__name",choices= (("adidas","adidas"),("nike","nike"),
		("godass","godass"),("converse","converse"),("puma","puma")))
	color = CharFilter(field_name="name", lookup_expr="icontains")

	class Meta:
		model = Color
		exclude = ['name','id','date_created','product','main_image']
		

