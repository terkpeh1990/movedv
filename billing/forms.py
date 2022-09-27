from django import forms
from .import models
from .models import Category,Product, Profile,Account_code
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm


User = get_user_model()

class DateInput(forms.DateInput):
    input_type = 'date'

class CategoryForm(forms.ModelForm):
    name = forms.CharField(label=False)

    class Meta:
        model = models.Category
        fields = ('name', )


class ProductForm(forms.ModelForm):
    name = forms.CharField(label=False)
    category = forms.ModelChoiceField(
        queryset=Category.objects.order_by('name'),label=False)
    office = forms.DecimalField(decimal_places=2,label=False)
    hq = forms.DecimalField(decimal_places=2,label=False)
    
    class Meta:
        model = models.Product
        fields = ('name', 'category', 'office' ,  'hq')


class CustomerForm(forms.ModelForm):
    name = forms.CharField(label=False)
    phone = forms.CharField(label=False)
    class Meta:
        model = models.Customer
        fields = ('name', 'phone')

class OrderdetailsForm(forms.ModelForm):
    product = forms.ModelChoiceField(
        queryset=Product.objects.order_by('name'),label=False)
    class Meta:
        model = models.Order_Details
        fields = ('product',)      

class PaymentForm(forms.ModelForm):
    money = forms.DecimalField(decimal_places=2,label=False)
    class Meta:
        model = models.Order
        fields = ('money',)

class PvForm(forms.ModelForm):
    description = forms.CharField(label=False)
    class Meta:
        model = models.Pv
        fields = ('description',)    

class Pv_detailsForm(forms.ModelForm):
    description = forms.CharField(label=False)
    amount = forms.CharField(label=False)
    class Meta:
        model = models.Pv_details
        fields = ('description','amount',)    

class UserLoginForm(forms.Form):
    username = forms.CharField(label=False, widget=forms.TextInput(
        attrs={'placeholder': 'Username'}))
    password = forms.CharField(label=False, widget=forms.PasswordInput(
        attrs={'placeholder': 'Password'}))

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('Username or Password incorrect')
            if not user.check_password(password):
                raise forms.ValidationError('Username or Password incorrect')
            if not user.is_active:
                raise forms.ValidationError('Username or Password incorrect')
        return super(UserLoginForm, self).clean(*args, **kwargs)

    class Meta():
        model = models.User
        fields = ('username', 'password')  