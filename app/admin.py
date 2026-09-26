from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Tag)
admin.site.register(Ad)
admin.site.register(Product)
admin.site.register(Color)
admin.site.register(Image)
admin.site.register(Size)
admin.site.register(Review)