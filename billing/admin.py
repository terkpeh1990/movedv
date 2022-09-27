from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Profile)
admin.site.register(Account_code)
admin.site.register(Trip)
admin.site.register(Revenue)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Order_Details)