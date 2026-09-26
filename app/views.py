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
def get_season (now):
	year = now.year
	seasons = {
		'winter' : (date(year=year-1,month=12,day=21),date(year=year,month=3,day=20)),
		'spring' : (date(year=year,month=3,day=21),date(year=year,month=6,day=20)),
		'summer' : (date(year=year,month=6,day=21),date(year=year,month=9,day=20)),
		'autumn' : (date(year=year,month=9,day=21),date(year=year,month=12,day=20)),
	}

	if seasons['winter'][0]<=now<=seasons['winter'][1]:
		return "winter"
	if seasons['spring'][0]<=now<=seasons['spring'][1]:
		return "spring"
	if seasons['summer'][0]<=now<=seasons['summer'][1]:
		return "summer"
	if seasons['autumn'][0]<=now<=seasons['autumn'][1]:
		return "autumn"



def free_undone_orders(orders):
	expiration_time = timedelta(hours=2)
	now = datetime.today()
	for order in orders:
		if order.total_items > 0:
			items = order.orderitem_set.all().order_by("-date_added")
			if now-items[0].date_added.replace(tzinfo=None) > expiration_time:
				for item in items:
					item.size.quantity += item.quantity
					item.size.save()
					item.delete()




# Create your views here.



def home(request):

	# to prevent custumers keeping products  too long 
	free_undone_orders(Order.objects.filter(closed=False))


	#query an inclosed order of an authenticated user for header.html return none in context order var
	order = None						
	if request.user.is_authenticated:										
		if request.user.customer.order_set.filter(closed=False).exists():
			order = request.user.customer.order_set.get(closed=False)

	orders = Order.objects.filter(closed=False)

	ads = Ad.objects.all() 
	try:
		info_ribbon = random.choice(ads)
	except:
		info_ribbon = None
	products = Product.objects.all()
	popular_products = products.order_by('-popularity')
	popular_products = popular_products[:4]
	new_arivalls = products.order_by('-date_created')
	new_arivalls = new_arivalls[:4]
	SEASON = get_season(date.today())
	season = products.filter(tags__name = SEASON )
	season = season[:4]
	style = products.filter(tags__name = 'style')
	style = style[:4]

	context = {'info_ribbon':info_ribbon, 'popular_products':popular_products,
	'new_arivalls':new_arivalls ,'season':season, 'style':style ,'order':order}

	return render(request,'app/index.html', context)




def collection(request,pk):

	order = None					
	if request.user.is_authenticated:
		if request.user.customer.order_set.filter(closed=False).exists():
			order = request.user.customer.order_set.get(closed=False)

	colors = Color.objects.all()

	tags = ["man","woman","adidas","nike","godass","style"]
	root = ""
	if pk in tags:
		for tag in tags:
			if pk == tag:
				colors = colors.filter(product__tags__name=tag)
				root = pk
				break
	elif pk == "new":
		colors = colors.order_by('-date_created')
	elif pk == "season":
		SEASON = get_season(date.today())
		colors = colors.filter(product__tags__name=SEASON)
		root = pk


	product_filter =  ColorFilter(request.GET, queryset=colors)
	colors = product_filter.qs
	if request.method == "GET":
		if request.GET.get("size") in ("36","37","38","39","40","41","42","43","44"):
			for color in colors:
				if not color.size_set.filter(name=request.GET.get("size")).exists():
					colors=colors.exclude(id=color.id)
		if request.GET.get("sort") == "newest":
			colors = colors.order_by("-date_created")
		elif request.GET.get("sort") == "price low to high":
			colors = colors.order_by("product__final_price")
		elif request.GET.get("sort") == "price high to low":
			colors = colors.order_by("-product__final_price")
		elif request.GET.get("sort") == "popular":
			colors = colors.order_by("-product__popularity")


	p = Paginator(colors,20)
	num_page = request.GET.get("page",1)
	try:
		page = p.page(num_page)
	except:
		page = p.page(1)

	context = {'colors':colors, 'page':page ,'order':order, 'root':root}

	return render(request,'app/collection.html',context)




def view (request,pk):

	order = None
	if request.user.is_authenticated:
		if request.user.customer.order_set.filter(closed=False).exists():
			order = request.user.customer.order_set.get(closed=False)

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

	tag = ""    #in case we dont have a tag
	if product.tags.all().count() > 0:
		tag = random.choice(product.tags.all()).name
	related_products = Product.objects.filter(tags__name = tag)
	related_products = related_products[:4]


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


	context = {'product':product , 'sizes':sizes, 'color':color, 'images':images, 'order':order,
	 'related_colors':related_colors  ,'related_products':related_products,
	 'out_of_stock':out_of_stock , 'reviews':reviews ,'form':form}

	return render(request, 'app/view.html' , context)




@login_required(login_url='login')
def bag(request):
	DELIVERY_COST = 500

	order ,create = request.user.customer.order_set.get_or_create(closed=False)
	items = order.orderitem_set.all()

	if request.method == "POST":
		try:
			quantity = int(request.POST.get("quantity"))
			if quantity > 0 and Size.objects.filter(name=request.POST.get("size"),
								color__name=request.POST.get("color"),
								color__product__name=request.POST.get("product")).exists():

				size = Size.objects.get(name=request.POST.get("size"),
								color__name=request.POST.get("color"),
								color__product__name=request.POST.get("product"))

				size.color.product.popularity+=1
				size.color.product.save()

				if size.quantity > 0:
					item ,create = OrderItem.objects.get_or_create(size=size,order=order)

					if quantity > size.quantity:
						quantity = size.quantity
					if quantity > 9-item.quantity:
						quantity = 9-item.quantity
						messages.info(request,"you have reached the maximum quantity for one product")
					
					item.quantity += quantity
					item.save()
					size.quantity -= quantity
					size.save()
				else:
					messages.info(request,"one item is out of stock")
		except:
			pass

	total_cost= order.total_cost+DELIVERY_COST


	if items.count() == 1 : 
		first_item_tag_name = items.first().size.color.product.tags.first().name
		pick_for_you_products = Product.objects.filter(tags__name=first_item_tag_name)
	elif items.count() > 1 :
		average_item_price = order.total_cost/order.total_items
		pick_for_you_products = Product.objects.filter(price__lte=average_item_price)
	else:
		pick_for_you_products =[]
  	
	pick_for_you_products = pick_for_you_products[:4]


	context = {'order':order,'items':items, "pick_for_you_products":pick_for_you_products,
	'DELIVERY_COST':DELIVERY_COST, 'total_cost':total_cost}

	return render(request,'app/shopping_bag.html', context)





@login_required(login_url='login')
def add(request,pk):

	try:
		item = OrderItem.objects.get(id=pk)
	except:
		return redirect('home')

	if request.user.customer == item.order.customer:	
		size = item.size
		if size.quantity > 0 and item.quantity < 9:
			item.quantity +=1
			item.save()
			size.quantity -=1
			size.save()
		else:
			if size.quantity == 0:
				messages.info(request,"one item is out of stock")
			if item.quantity >= 9:
				messages.info(request,"you have reached the maximum quantity for one product")
			
		return redirect('bag')

	return redirect('home')




@login_required(login_url='login')
def sub(request,pk):

	try:
		item = OrderItem.objects.get(id=pk)
	except:
		return redirect('home')

	if request.user.customer == item.order.customer:
		size = item.size
		if item.quantity > 0:
			item.quantity-=1
			item.save()
			size.quantity+=1
			size.save()

			if item.quantity == 0:
				item.delete()	
		
		return redirect('bag')

	return redirect('home')





@login_required(login_url='login')
def checkout(request):

	DELIVERY_COST = 500

	order ,create = request.user.customer.order_set.get_or_create(closed=False)
	if order.total_items <= 0 :
		return redirect('bag')
	items = order.orderitem_set.all()
	total_cost= order.total_cost+DELIVERY_COST

	context = {'order':order,'items':items,
	'DELIVERY_COST':DELIVERY_COST, 'total_cost':total_cost}

	if request.method == "POST":
		email = request.POST.get("email")
		if email == "":
			email = order.customer.email
		form = ShippingAddressForm({
			'order':order,
			'first_name':request.POST.get("first_name"),
			'last_name':request.POST.get("last_name"),
			'address':request.POST.get("address"),
			'wilaya':request.POST.get("wilaya"),
			'email':email,
			'phone':request.POST.get("phone"),
			'payment_method':request.POST.get("payment_method")
			})

		if form.is_valid():
			form.save()
			order.closed = True
			order.save()


			shipping = order.shippingaddress_set.all().get(order=order)
			context['shipping'] = shipping
			context['request'] = request

#email sending
			#email sending for customer + shopers
			template_customer = render_to_string('app/customer_mail.html',context)
			template_staff = render_to_string('app/staff_mail.html',context)
			customer_email = EmailMessage(
											'Order Details',
											template_customer,
											settings.EMAIL_HOST_USER,
											[form.cleaned_data.get("email")]
											)
			customer_email.fail_silently = False
			customer_email.send()
									
			stuff_email = EmailMessage(
											'New Order',
											template_staff,
											settings.EMAIL_HOST_USER,
											['oussamaboukhetala@gmail.com']
											)
			stuff_email.fail_silently = False
			stuff_email.send()
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
