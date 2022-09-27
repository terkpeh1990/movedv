from django.contrib.auth.models import AbstractUser, User

from django.db import models
from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.sessions.models import Session
import datetime
from .utils import incrementor,revenue_incrementor
from crum import get_current_user
from simple_history.models import HistoricalRecords

# Create your models here.

User = settings.AUTH_USER_MODEL

class UserSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    session = models.OneToOneField(Session, on_delete=models.CASCADE)


class Profile(models.Model):
    user = models.OneToOneField(
        User, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    is_manager = models.BooleanField(default=False)
    is_standard = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.CharField(max_length=250, primary_key=True)
    name = models.CharField(max_length=250)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    office = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    hq = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    history = HistoricalRecords()


    def __str__(self):
        return self.name


    def save(self):

        if not self.id:
            number = incrementor()
            self.id = number()
            while Product.objects.filter(id=self.id).exists():
                self.id = number()
        self.unit_price = self.office + self.hq
        super(Product, self).save()


class Customer(models.Model):
    id = models.CharField(max_length=250, primary_key=True)
    name = models.CharField(max_length=250)
    phone = models.CharField(max_length=20)


    history = HistoricalRecords()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        if not self.id:
            number = incrementor()
            self.id = number()
            while Customer.objects.filter(id=self.id).exists():
                self.id = number()
        super(Customer, self).save( *args, **kwargs)

class Trip(models.Model):
    stat =(
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )
    trip_date = models.DateField()
    name = models.CharField(max_length=250)
    status = models.CharField(max_length=10, choices=stat)

    class Meta():
        ordering = ('-name', )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            number = incrementor()
            self.name = "Trip"+ str(number())
            while Trip.objects.filter(name=self.name).exists():
                self.name= "Trip"+ str(number())
        super(Trip, self).save( *args, **kwargs)


class Order(models.Model):


    id = models.CharField(max_length=250, primary_key=True)
    order_date = models.DateField(null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    gross_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    trip = models.ForeignKey(Trip, on_delete= models.CASCADE, null=True, blank=True)
    money_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    money = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    money_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    correction = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, related_name='ORcreatedby', blank=True, null=True,
                                   default=None)
    modified = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, related_name='ORmodifiedby', blank=True, null=True,
                                    default=None)
    history = HistoricalRecords()




    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        user = get_current_user()
        self.balance = self.gross_price - self.money_paid
        if user and not user.pk:
            user = None
        if not self.id:
            number = incrementor()
            self.id = str(number())
            while Order.objects.filter(id=self.id).exists():
                self.id = str(number())
            self.created_by = user
        self.modified_by = user

        super(Order, self).save( *args, **kwargs)

class Order_Details(models.Model):
    product = models.ForeignKey(Product, on_delete= models.DO_NOTHING)
    office = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    hq = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip,models.CASCADE)

    history = HistoricalRecords()
    def __str__(self):
        return self.product.name


class Invoice(models.Model):
    id = models.CharField(max_length=250, primary_key=True)
    order_id= models.ForeignKey(Order, on_delete=models.DO_NOTHING)
    office = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    hq = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.id:
            number = incrementor()
            self.id = number()
            while Invoice.objects.filter(id=self.id).exists():
                self.id = number()
        super(Invoice, self).save(*args, **kwargs)


class loginrecords(models.Model):
    user = models.CharField(max_length=250)
    is_standard = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    date = models.DateField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.user

class Account_code(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50)

    def __str__(self):
        return self.code

class Revenue(models.Model):

    id = models.CharField(max_length=100, primary_key=True)
    account_code = models.ForeignKey(Account_code, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    hq = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    office = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE,null=True, blank=True)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE,null=True, blank=True)

    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.amount)

    def save(self, *args, **kwargs):
        if not self.id:
            number = revenue_incrementor()
            self.id = number()
            while Revenue.objects.filter(id=self.id).exists():
                self.id = number()
        super(Revenue, self).save(*args, **kwargs)


class Expenditure(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    description=models.CharField(max_length=2000,null=True, blank=True)
    account_code = models.ForeignKey(Account_code, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE,null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return str(self.amount)

    def save(self, *args, **kwargs):


        if not self.id:
            number = revenue_incrementor()
            self.id = number()
            while Expenditure.objects.filter(id=self.id).exists():
                self.id = number()
        super(Expenditure, self).save(*args, **kwargs)

class Pv(models.Model):
    stat =(
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Cancelled','Cancelled')
    )
    id = models.CharField(max_length=100, primary_key=True)
    description=models.CharField(max_length=250)
    account_code = models.ForeignKey(Account_code,null=True, blank=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=15,choices=stat)
    trip = models.ForeignKey(Trip,null=True, blank=True, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.description

    def save(self, *args, **kwargs):


        if not self.id:
            number = revenue_incrementor()
            self.id = number()
            while Pv.objects.filter(id=self.id).exists():
                self.id = number()
        super(Pv, self).save(*args, **kwargs)

class Pv_details(models.Model):
    description=models.CharField(max_length=250)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pv = models.ForeignKey(Pv, on_delete=models.CASCADE,null=True, blank=True)

    def __str__(self):
        return self.description


