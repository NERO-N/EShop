from django.urls import path
from .views import *

from django.contrib.auth import views as auth_views


urlpatterns = [
	path('' , home , name="home"),
	path('collection/<str:pk>/' , collection , name="collection"),
	path('view/ <str:pk> /', view , name="view"),
	path('shopping_bag/', bag , name="bag"),
	path('checkout/' , checkout , name="checkout"),

	path('login/' , login_page , name="login"),
	path('register/'  , register, name="register"),
	path('logout/' , logout_page, name="logout"),

	path('add/<str:pk>/', add, name="add"),
	path('sub/<str:pk>/', sub, name="sub"),

	path('edit/<str:pk>/', edit_review, name="edit" ),
	path('delete/<str:pk>/', delete_review, name="delete"),

	path('reset_password/',
	 auth_views.PasswordResetView.as_view(template_name="app/password_reset.html"),
	  name="reset_password"),
	path('reset_password_sent/',
	 auth_views.PasswordResetDoneView.as_view(template_name="app/password_reset_sent.html"),
	  name="password_reset_done"),
	path('reset/<uidb64>/<token>/',
	 auth_views.PasswordResetConfirmView.as_view(template_name="app/password_reset_confirm.html"),
	  name="password_reset_confirm"),
	path('reset_password_complete/',
	 auth_views.PasswordResetCompleteView.as_view(template_name="app/password_reset_complete.html"),
	  name="password_reset_complete"),
]