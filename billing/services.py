from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.contrib import messages


def create_category(request):
    if request.method =="POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category Added")
            return redirect("billing:manage_category")
    else:
        form = CategoryForm()
    
    template = "billing/create_category.html"
    context ={
        'form':form,
    }
    return render(request,template,context)

def edit_category(request,pk):
    category = Category.objects.get(id=pk)
    if request.method =="POST":
        form = CategoryForm(request.POST,instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category Updated")
            return redirect("billing:manage_category")
    else:
        form = CategoryForm(instance=category)
    
    template = "billing/edit_category.html"
    context ={
        'form':form,
    }
    return render(request,template,context)

def create_product(request):
    if request.method =="POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Service Added")
            return redirect("billing:manage_product")
    else:
        form = ProductForm()
    
    template = "billing/create_product.html"
    context ={
        'form':form,
    }
    return render(request,template,context)

def edit_product(request,pk):
    product = Product.objects.get(id=pk)
    if request.method =="POST":
        form = ProductForm(request.POST, instance= product)
        if form.is_valid():
            form.save()
            messages.success(request, "Service Updated")
            return redirect("billing:manage_product")
    else:
        form = ProductForm(instance=product)
    
    template = "billing/edit_product.html"
    context ={
        'form':form,
    }
    return render(request,template,context)

def manage_category(request):
    category = Category.objects.all()
    template = "billing/manage_category.html"
    context ={
        'category':category,
    }
    return render(request,template,context)

def manage_product(request):
    product = Product.objects.all()
    template = "billing/manage_product.html"
    context ={
        'product':product,
    }
    return render(request,template,context)