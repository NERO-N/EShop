from django.db import models
import uuid
from django.contrib.auth.models import User


# Create your models here.

class Customer(models.Model):
	user = models.OneToOneField(User , on_delete=models.CASCADE ,null=True)
	name = models.CharField(max_length=80, null=True) 
	email = models.EmailField(max_length=80, null=True)
	allowed_to_comment = models.BooleanField(default=True, null=True)
	date_created = models.DateTimeField(auto_now_add=True)
	id = models.UUIDField(primary_key=True, default=uuid.uuid4,
						 			unique=True, editable=False)

	def __str__ (self):
		return self.name


class Order(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL ,null=True)
	closed = models.BooleanField(default=False, null=True)
	date_created = models.DateTimeField(auto_now_add=True)
	id = models.UUIDField(primary_key=True, default=uuid.uuid4,
						 			unique=True, editable=False)


	def __str__(self):
		try:
			return str(self.date_created)
		except:
			return "order of unknown customer"

	def get_total_items(self):
		items = self.orderitem_set.all()
		return sum([ item.quantity for item in items])


	def get_total_cost(self):
		items = self.orderitem_set.all()
		return sum([ item.total_cost for item in items])

	total_items = property(get_total_items)
	total_cost = property(get_total_cost)





class ShippingAddress(models.Model):
	
	order = models.ForeignKey(Order, on_delete=models.SET_NULL ,null=True)
	first_name = models.CharField(max_length=20, null=True)
	last_name = models.CharField(max_length=20, null=True)
	wilaya = models.CharField(max_length=30, null=True)
	address = models.CharField(max_length=80, null=True)
	email = models.EmailField(max_length=80, null=True)
	phone = models.CharField(max_length=15, null=True)
	payment_method = models.CharField(max_length=200, default='Hand To Hand', null=True)
	date_created = models.DateTimeField(auto_now_add=True)
	id = models.UUIDField(primary_key=True, default=uuid.uuid4,
						 			unique=True, editable=False)

	def __str__ (self):
		return str(self.date_created)


class Tag(models.Model):
	name = models.CharField(max_length=20, null=True)
	date_created = models.DateTimeField(auto_now_add=True)
	id = models.UUIDField(primary_key=True, default=uuid.uuid4,
						 			unique=True, editable=False)

	def __str__ (self):
		return self.name

class Ad(models.Model):
	content = models.CharField(max_length=200, null=True)
	date_created = models.DateTimeField(auto_now_add=True)
	id = models.UUIDField(primary_key=True, default=uuid.uuid4,
						 			unique=True, editable=False)

	def __str__ (self):
		return self.content

class Product(models.Model): 
	name = models.CharField(max_length=30, null=True)
	price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
	final_price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
	description = models.TextField(max_length=500, null=True)
	popularity = models.IntegerField(default=0, null=True)
	tags = models.ManyToManyField(Tag)
	date_created = models.DateTimeField(auto_now_add=True)
	id = models.UUIDField(primary_key=True, default=uuid.uuid4,
						 			unique=True, editable=False)

	def __str__ (self):
		return self.name

	def get_colors(self):
		return self.color_set.count()

	def get_default_color(self):
		return self.color_set.order_by("date_created").first()



	colors = property(get_colors)
	default_color = property(get_default_color)




class Color(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE ,null=True)
	name = models.CharField(max_length=200, null=True)
	main_image = models.ImageField(null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True)
	id = models.UUIDField(primary_key=True, default=uuid.uuid4,
						 			unique=True, editable=False)

	def __str__ (self):
		return self.product.name+" "+self.name

	def get_image_URL(self):
		try:
			return self.main_image.url
		except:
			return ''

	main_image_URL = property(get_image_URL)






class Image (models.Model):
	color = models.ForeignKey(Color, on_delete=models.CASCADE ,null=True)
	image = models.ImageField(null=True, blank=True)
	date_created = models.DateTimeField(auto_now_add=True)
	id = models.UUIDField(primary_key=True, default=uuid.uuid4,
						 			unique=True, editable=False)
	def __str__ (self):
		return self.color.product.name+" "+self.color.name

	def get_image_URL(self):
		try:
			return self.image.url
		except:
			return ''

	image_URL = property(get_image_URL)




class Size(models.Model):
	color = models.ForeignKey(Color, on_delete=models.CASCADE ,null=True)
	name = models.CharField(max_length=200, null=True)
	quantity = models.IntegerField(default=0, null=True)
	date_created = models.DateTimeField(auto_now_add=True)
	id = models.UUIDField(primary_key=True, default=uuid.uuid4,
						 			unique=True, editable=False)

	def __str__ (self):
		return self.color.product.name+" "+self.color.name+" "+self.name


class Review(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL ,null=True)
	product = models.ForeignKey(Product , on_delete=models.SET_NULL ,null=True)
	content  = models.TextField(max_length=400, null=True)
	date_created = models.DateTimeField(auto_now_add=True)
	date_edited = models.DateTimeField(auto_now=True)
	id = models.UUIDField(primary_key=True, default=uuid.uuid4,
						 			unique=True, editable=False)

	def __str__ (self):
		try:
			return self.customer.name+" for "+self.product.name
		except:
			return "review from unknown customer or product" 


class OrderItem(models.Model):
	size = models.ForeignKey(Size, on_delete=models.SET_NULL ,null=True)
	order = models.ForeignKey(Order , on_delete=models.SET_NULL ,null=True)
	quantity = models.IntegerField(default=0, null=True)
	date_added = models.DateTimeField(auto_now_add=True)
	id = models.UUIDField(primary_key=True, default=uuid.uuid4,
						 			unique=True, editable=False)

	def __str__ (self):
		try:
			return (str(self.order.date_created))
		except:
			return "item unknown"

	def get_total_cost(self):
		return self.quantity*self.size.color.product.final_price


	total_cost = property(get_total_cost)