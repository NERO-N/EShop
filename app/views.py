from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from django.core.mail import EmailMessage				#to send mails
from django.conf import settings
from django.template.loader import render_to_string

import random
from .decorators import *
from .models import *
from .forms import *
from .filters import *


from datetime import date, datetime, timedelta


# Create your views here.



def home(request):

	products = Product.objects.all()
	product_filter =  ProductFilter(request.GET, queryset=products)
	products = product_filter.qs

	context = {'products':products}

	return render(request,'app/index.html', context)



def view (request,pk):

	try:
		color = Color.objects.get(id=pk)
	except:
		return redirect('home')

	product = color.product
	related_colors = product.color_set.all()
	images = color.image_set.all()
	sizes = color.size_set.all() 
	reviews = Review.objects.filter(product=product).order_by("-date_edited")
	reviews = reviews[:10]

	out_of_stock = True
	for size in sizes:
		if size.quantity > 0:
			out_of_stock = False

	form = ReviewForm()
	if request.method == "POST":
		if request.user.is_authenticated: 
			if request.user.customer.allowed_to_comment:
				form = ReviewForm({'customer':request.user.customer, 'product':product
									,'content':request.POST.get("content")})
				if form.is_valid():
					form.save()
			else:
				messages.error(request,"you are not allowed to comment")
		else:
			return redirect('login')


	context = {'product':product , 'sizes':sizes, 'color':color, 'images':images, 
	 'related_colors':related_colors ,'out_of_stock':out_of_stock ,
	  'reviews':reviews ,'form':form}

	return render(request, 'app/view.html' , context)



def checkout(request):
	delivery_tarification = {
		"Adrar":1200,"Chlef":880,"Laghouat":990,"Oum El Bouaghi":880,"Batna":880,"Bejaia":800,"Biskra":880,
		"Bechar":1100,"Blida":650,"Bouira":800,"Tebessa":900,"Tlemcen":850,"Tiaret":880,"Tizi Ouzou":800,
		"Alger":400,"Djelfa":990,"Jijel":880,"Setif":850,"Saida":880,"Skikda":880,"Sidi Bel-Abbes":880,
		"Annaba":800,"Geulma":880,"Constantine":800,"Medea":800,"Mostaganem":880,"M'sila":880,"Mascara":880,
		"Ourgla":900,"Oran":800,"El bayadh":1100,"Bordj-BouArreridj":800,"Boumerdes":700,"El-Taref":880,"Tissemsilt":880,
		"El-Oued":990,"Khenchela":880,"Souk-Ahras":880,"Tipaza":700,"Mila":880,"Ain-Defla":880,"Naama":1100,
		"Ain Temouchent":880,"Ghardaia":990,"Relizane":880,
	}

	DELIVERY_COST = 0
	total_cost = 0
	item = None

	if request.method == "GET":
		try:
			quantity = int(request.GET.get("quantity"))
			if quantity > 0 and Size.objects.filter(name=request.GET.get("size"),
								color__name=request.GET.get("color"),
								color__product__name=request.GET.get("product")).exists():

				size = Size.objects.get(name=request.GET.get("size"),
								color__name=request.GET.get("color"),
								color__product__name=request.GET.get("product"))

				if size.quantity > 0:
					order = Order.objects.create(closed=False)
					item = OrderItem.objects.create(size=size,order=order)

					if quantity > size.quantity:
						quantity = size.quantity
						messages.info(request,str(item.size.quantity)+"  : الكمية المتوفرة   ")
					if quantity > 9 :
						quantity = 9 
						messages.info(request,"you have reached the maximum quantity for one product")
					
					item.quantity = quantity
					item.save()
					total_cost= item.total_cost+DELIVERY_COST

				else:
					messages.info(request,"one item is out of stock")
		except:
			pass

	context = {'item':item,
	'DELIVERY_COST':DELIVERY_COST, 'total_cost':total_cost}

	if request.method == "POST":
		try :
			if OrderItem.objects.filter(id=request.POST.get("item")).exists() and request.POST.get("wilaya") in delivery_tarification and request.POST.get("field") == "":
				item = OrderItem.objects.get(id=request.POST.get("item"))
				DELIVERY_COST = delivery_tarification[request.POST.get("wilaya")]
			else:
				return redirect('home')
		except:
			return redirect('home')

		if item.size.quantity < item.quantity:
			messages.info(request,"(ERROR) "+str(item.size.quantity)+"  :الكمية المتوفرة   ")
			return render(request,'app/checkout.html', context)

		email = request.POST.get("email")
		if email == "":
			email = "none@email.com"
		form = ShippingAddressForm({
			'order':item.order,
			'first_name':request.POST.get("first_name"),
			'last_name':request.POST.get("last_name"),
			'address':request.POST.get("address"),
			'wilaya':request.POST.get("wilaya"),
			'email':email,
			'phone':request.POST.get("phone"),
			'payment_method':"HandToHand"
			})

		if form.is_valid():
			form.save()
			item.order.closed = True
			item.order.save()

			item.size.quantity -= item.quantity
			item.size.save()		

			total_cost= item.total_cost+DELIVERY_COST

			shipping = item.order.shippingaddress_set.all().get(order=item.order)


			context = {'item':item, 'shipping':shipping,
			'DELIVERY_COST':DELIVERY_COST, 'total_cost':total_cost}
#email sending
			# template_staff = render_to_string('app/staff_mail.html',context)					
			# stuff_email = EmailMessage(
			# 								'New Order',
			# 								template_staff,
			# 								settings.EMAIL_HOST_USER,
			# 								['oussamaboukhetala@gmail.com']
			# 								)
			# stuff_email.fail_silently = False
			# stuff_email.send()
#/email sending

			return render(request,'app/order_done.html', context)
			
		context["form"] = form



	return render(request,'app/checkout.html', context)



@unauthenticated_required
def register(request):
	form = CreateUserForm()

	if request.method == "POST":
		form = CreateUserForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request,"Account was successfuly created")
			return redirect('login')

	context = {'form': form}

	return render(request,'app/register.html' , context)	




@unauthenticated_required
def login_page(request):

	if request.method == "POST":
		username = request.POST.get("username")
		password = request.POST.get("password")

		user = authenticate(request , username=username, password=password )
		if user is not None:
			login(request,user)  
			try:
				request.user.customer 
			except:
				Customer.objects.create(user = request.user,
										name = request.user.username,
										email = request.user.email,
										)			

			return redirect('home')

		else:
			messages.info(request,"your Username or Password is not correct")

	return render(request,'app/login.html' )



def logout_page(request):
	logout(request)
	return redirect('home')



@login_required(login_url='login')
def edit_review(request,pk):

	try:
		review = Review.objects.get(id=pk)
	except:
		return redirect('home')

	if review.customer == request.user.customer:
		form = ReviewForm(instance=review)
		if request.method == "POST":
			form = ReviewForm({'customer':request.user.customer,'product':review.product,
				'content':request.POST.get("content")},instance=review)
			if form.is_valid():
				form.save()
				return redirect('/view/ '+str(review.product.default_color.id)+' /#reviews')

		context = {'form':form , 'review':review }

		return render(request,'app/edit_review.html',context)

	return redirect('/view/ '+str(review.product.default_color.id)+' /#reviews')




@login_required(login_url='login')
def delete_review(request,pk):
	try:
		review = Review.objects.get(id=pk)
	except:
		return redirect('home')

	if review.customer == request.user.customer:
		review.delete()

	#return redirect('view',pk=review.product.default_color.id)
	return redirect('/view/ '+str(review.product.default_color.id)+' /#reviews')
