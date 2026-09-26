import django_filters
from django_filters import CharFilter,NumberFilter,ChoiceFilter
from django import forms
from .models import *


class ProductFilter(django_filters.FilterSet):
	
	product_name = CharFilter(field_name="name", lookup_expr="icontains")
	

	class Meta:
		model = Product
		fields = "__all__"
		

