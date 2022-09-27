from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage  # To upload Profile Picture
from django.urls import reverse
from django.db.models import Sum

from django.db.models.functions import TruncMonth
from .forms import *
from .models import *
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, View, CreateView
from django.views.generic.edit import CreateView, UpdateView
from django.http import JsonResponse
from django.core import serializers
import datetime
from django.contrib.auth.decorators import login_required
from dvla_billing.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
from twilio.rest import Client
from .filters import *
from .thread import *

def create_customer(request):
    if request.method == "POST":
        form =CustomerForm(request.POST)
        if form.is_valid():
            today = datetime.datetime.now().date()
            customer = form.save()
            trip = Trip.objects.get(status = "Active")
            order = Order.objects.create(customer=customer, order_date=today,trip=trip)
            request.session['id'] = order.id
            return redirect('billing:orderitems')
    else:
        form = CustomerForm()
    template ='billing/create_customer.html'
    context ={
        'form':form
    }
    return render(request,template,context)


class orderitems(CreateView):
    model = Order_Details
    form_class = OrderdetailsForm
    template = 'billing/create_orderitems.html'

    def get(self, *args, **kwargs):
        if self.request.session['id']:
            order_id = self.request.session['id']
            order = Order.objects.get(id=order_id)
            form = self.form_class()
            detail = Order_Details.objects.filter(order_id=order)
            if detail:
                gross_total = detail.aggregate(cc=Sum('unit_price'))
                # order.gross_price = gross_total['cc']
                # order.save()
            else:
                gross_total = 0.00
                # order.gross_price = gross_total
                # order.save()
            return render(self.request, self.template, {"form": form, "detail": detail,  "gross_total": gross_total, "order": order})

    def post(self,  *args, **kwargs):
        if self.request.is_ajax and self.request.method == "POST":
            form = self.form_class(self.request.POST)
            if self.request.session['id']:
                order_id = self.request.session['id']
                order = Order.objects.get(id=order_id)
            if form.is_valid():

                instance = form.save(commit=False)
                product = Product.objects.get(name=instance.product)
                instance.order_id = order
                instance.unit_price = product.unit_price
                # order.gross_price += instance.unit_price
                order.save
                instance.hq = product.hq
                instance.office = product.office
                trip = Trip.objects.get(status = "Active")
                instance.trip = trip
                order.gross_price += instance.unit_price
                order.save()
                instance.save()
                ser_instance = serializers.serialize('json', [instance, ])
                return JsonResponse({"instance": ser_instance}, status=200)
            else:
                return JsonResponse({"error": form.errors}, status=400)
        return JsonResponse({"error": ""}, status=400)

    def form_valid(self, form):
        messages.success(self.request, 'Activity item added')
        return super().form_valid(form)

def deletes_items(request,pk):
    pro = Order_Details.objects.get(id=pk)
    order = Order.objects.get(id=pro.order_id)
    order.gross_price -= pro.unit_price
    order.save()
    pro.delete()
    return redirect('billing:orderitems')

def checkout(request):
    if request.session['id']:
        order_id = request.session['id']
        order = Order.objects.get(id =order_id)
        detail = Order_Details.objects.filter(order_id=order.id)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            if order.gross_price > form.cleaned_data['money'] or order.gross_price < form.cleaned_data['money']:
                messages.success(request,"Amount Entered Cannot be less or more  than total transaction")
                return redirect('billing:checkout')
            else:
                today = datetime.datetime.now()
                order.money_paid += form.cleaned_data['money']
                order.save()
                hq = detail.aggregate(cc=Sum('hq'))
                office = detail.aggregate(cc=Sum('office'))

                try:
                    code = Account_code.objects.get(code="Revenue")
                except Account_code.DoesNotExist:
                    code = Account_code.objects.create(code="Revenue")


                Revenue.objects.create(
                    account_code=code, amount=order.money_paid,hq=hq['cc'],office=office['cc'],trip = order.trip,order_id =order)
                messages.success(request, 'Payment made Sucessfully')
                SendMessageThread(detail).start()


                return redirect('billing:checkout')



    else:
        form = PaymentForm()
    template = 'billing/checkout.html'
    context = {
        'order': order,
        'detail': detail,
        'form': form,
    }
    return render(request,template,context)

def close(request):
    if request.session['id']:
        try:
            del request.session['id']
            return redirect('billing:manage_orders')
        except KeyError:
            return redirect('billing:manage_orders')

def closed(request):
    return redirect('billing:manage_orders')



def manage_orders(request):
    try:
        trip = Trip.objects.get(status= "Active")
        order = Order.objects.filter(trip=trip.id)
        attendance = Order.objects.filter(trip=trip.id,gross_price__gt=0.00).count()
        revenue = Revenue.objects.filter(trip=trip.id)
        trip_revenue =revenue.aggregate(cc =Sum('amount'))
    except Trip.DoesNotExist:
        order = Order.objects.all()
        attendance = Order.objects.all().count()
        revenue = Revenue.objects.all()
        trip_revenue =revenue.aggregate(cc =Sum('amount'))



    template = 'billing/manage_orders.html'
    Context ={
        'order':order,
        'attendance':attendance,
        'trip_revenue':trip_revenue,
    }
    return render(request,template,Context)

def search_orders(request):

    order = Order.objects.all()

    template = 'billing/search.html'
    Context ={
        'order':order,

    }
    return render(request,template,Context)

def Vew_order(request,pk):

    order = Order.objects.get(id=pk)
    detail = Order_Details.objects.filter(order_id=order.id)
    template = 'billing/view_order.html'
    context = {
        'order': order,
        'detail': detail,
    }
    return render(request, template, context)


def allexpenses(request):
    today = datetime.datetime.now()
    ord = Expenditure.objects.all().order_by('-id')
    total = ord.aggregate(cc=Sum('amount'))


    myFilter = ExpenditureFilter(request.GET, queryset=ord)
    ord = myFilter.qs
    total = myFilter.qs.aggregate(cc=Sum('amount'))


    template = 'billing/expenditure.html'
    context = {
        'ord': ord,
        'total': total,
        'myFilter': myFilter,
    }
    return render(request, template, context)


def allrevenue(request):
    today = datetime.datetime.now()
    ord = Revenue.objects.all().order_by('-id')
    total = ord.aggregate(cc=Sum('amount'))
    hq = ord.aggregate(cc=Sum('hq'))
    office =ord.aggregate(cc=Sum('office'))

    myFilter = RevenueFilter(request.GET, queryset=ord)
    ord = myFilter.qs
    total = myFilter.qs.aggregate(cc=Sum('amount'))
    hq = myFilter.qs.aggregate(cc=Sum('hq'))
    office =myFilter.qs.aggregate(cc=Sum('office'))

    template = 'billing/revenue.html'
    context = {
        'ord': ord,
        'total': total,
        'hq':hq,
        'office':office,
        'myFilter': myFilter,
    }
    return render(request, template, context)



def income_expenditure(request):
    acc= Account_code.objects.all()
    today = datetime.datetime.now()
    expenses = Expenditure.objects.values('account_code').annotate(
        month=TruncMonth('created_date'), monthly=Sum('amount')).order_by('month')
    income = Revenue.objects.values('account_code').annotate(
        month=TruncMonth('created_date'), monthly=Sum('amount'),monthlys=Sum('hq'),monthlyss=Sum('office')).order_by('month')

    ord = expenses
    ords = income
    total = Expenditure.objects.aggregate(expense=Sum('amount'))
    tot = Revenue.objects.all().aggregate(cc=Sum('amount'))
    hq = Revenue.objects.all().aggregate(hq=Sum('hq'))
    office =Revenue.objects.all().aggregate(office=Sum('office'))
    # if total['expense'] and tot['cc']:
    #     bf = tot['cc'] - total['expense']
    #     hqbf = hq['cc'] - total['expense']
    #     officebf = office['cc'] - total['expense']

    # elif not total['expense'] and tot['cc']:
    #     bf = tot['cc']
    #     hqbf = hq['cc']
    #     officebf = office['cc']

    # elif total['expense'] and not tot['cc']:
    #     bf = total['expense']
    #     hqbf =total['expense']
    #     officebf =total['expense']

    # elif not total['expense'] and not tot['cc']:
    #     bf = 0.00
    #     hqbf =0.00
    #     officebf =0.00

    myFilter = ExpenditureFilter(request.GET, queryset=ord)
    myFilter2 = RevenueFilter(request.GET, queryset=ords)
    ord = myFilter.qs
    ords = myFilter2.qs

    total = ord.aggregate(expense=Sum('amount'))
    tot = ords.aggregate(cc=Sum('amount'))
    hq= myFilter2.qs.aggregate(cc=Sum('hq'))
    office = myFilter2.qs.aggregate(cc=Sum('office'))

    # if total['expense'] and tot['cc']:
    #     bf = tot['cc'] - total['expense']
    #     hqbf = hq['cc'] - total['expense']
    #     officebf = office['cc'] - total['expense']

    # elif not total['expense'] and tot['cc']:
    #     bf = tot['cc']
    #     hqbf = hq['cc']
    #     officebf = office['cc']

    # elif total['expense'] and not tot['cc']:
    #     bf = total['expense']
    #     hqbf =total['expense']
    #     officebf =total['expense']

    # elif not total['expense'] and not tot['cc']:
    #     bf = 0.00
    #     hqbf =0.00
    #     officebf =0.00

    template = 'billing/income&expenditure.html'
    context = {
        'ord': ord,
        'ords': ords,
        'total': total,
        'hq':hq,
        'office':office,
        'tot': tot,
        # 'bf': bf,
        # 'hqbf':hqbf,
        # 'officebf':officebf,
        'myFilter': myFilter,
        'myFilter2': myFilter2,
        'acc':acc,

    }
    return render(request, template, context)

def create_pv(request):
    if request.method == "POST":
        form = PvForm(request.POST)
        if form.is_valid():
            cc=form.save(commit=False)
            cc.status = "Pending"
            try:
                code = Account_code.objects.get(code="Bills")
            except Account_code.DoesNotExist:
                code = Account_code.objects.create(code="Bills")
            cc.account_code = code
            trip = Trip.objects.get(status = "Active")
            cc.trip =trip
            cc.save()
            request.session['pv'] = cc.id
            return redirect('billing:pv_detail')
    else:
        form = PvForm()
    template = 'billing/create_pv.html'
    context = {
        'form':form,
    }
    return render(request,template,context)

class pv_detail(CreateView):
    model = Pv_details
    form_class = Pv_detailsForm
    template = 'billing/create_pvdetail.html'

    def get(self, *args, **kwargs):
        if self.request.session['pv']:
            order_id = self.request.session['pv']
            order = Pv.objects.get(id=order_id)
            form = self.form_class()
            detail = Pv_details.objects.filter(pv=order)
            if detail:
                gross_total = detail.aggregate(cc=Sum('amount'))
                # order.amount = gross_total['cc']
                # order.save()
            else:
                gross_total = 0.00
                order.gross_price = gross_total
                order.save()
            return render(self.request, self.template, {"form": form, "detail": detail,  "gross_total": gross_total, "order": order})

    def post(self,  *args, **kwargs):
        if self.request.is_ajax and self.request.method == "POST":
            form = self.form_class(self.request.POST)
            if self.request.session['pv']:
                order_id = self.request.session['pv']
                order = Pv.objects.get(id=order_id)
                details = Pv_details.objects.filter(pv=order.id)
            if form.is_valid():
                instance = form.save(commit=False)
                product = Account_code.objects.get(code="Bills")
                instance.pv = order
                tt= details.aggregate(cc=Sum('amount'))
                instance.save()
                order.amount +=instance.amount
                order.save()
                ser_instance = serializers.serialize('json', [instance, ])
                return JsonResponse({"instance": ser_instance}, status=200)
            else:
                return JsonResponse({"error": form.errors}, status=400)
        return JsonResponse({"error": ""}, status=400)

    def form_valid(self, form):
        messages.success(self.request, 'Activity item added')
        return super().form_valid(form)

def deletes_pvitems(request,pk):
    pro = Pv_details.objects.get(id=pk)
    pv = Pv.objects.get(id=pro.pv.id)
    pv.amount -=pro.amount
    pv.save()
    pro.delete()
    return redirect('billing:pv_detail')

def closepv(request):
    if request.session['pv']:
        try:
            del request.session['pv']
            return redirect('billing:manage_pv')
        except KeyError:
            return redirect('billing:manage_pv')


def manage_pv(request):
    pv = Pv.objects.all()
    template = 'billing/manage_pv.html'
    context={
        'pv':pv,
    }
    return render(request,template,context)

def pending_pv(request):
    pv = Pv.objects.filter(status = "Pending")
    template = 'billing/pending_pv.html'
    context={
        'pv':pv,
    }
    return render(request,template,context)

def View_pv(request,pk):

    order = Pv.objects.get(id=pk)
    detail = Pv_details.objects.filter(pv=order.id)
    template = 'billing/view_pv.html'
    context = {
        'order': order,
        'detail': detail,
    }
    return render(request, template, context)


def cancelled(request,pk):
    pv = Pv.objects.get(id=pk)
    pv.status = "Cancelled"
    pv.save()
    messages.success(request,'PV Cancelled')
    return redirect('billing:pending_pv')

def approve(request,pk):
    pv = Pv.objects.get(id=pk)
    pv.status = "Approved"
    trip = Trip.objects.get(status ="Active")
    Expenditure.objects.create(description=pv.description,account_code=pv.account_code,amount=pv.amount,trip=trip)
    pv.save()
    messages.success(request,'PV Approved')
    return redirect('billing:pending_pv')

def daily_sales(request):
    today = datetime.datetime.now().date()
    try:
        active_trip = Trip.objects.get(status="Active")
        sale = Revenue.objects.filter(trip = active_trip, created_date = today)
        total = sale.aggregate(cc=Sum('amount'))
    except Trip.DoesNotExist:
        sale = Revenue.objects.filter(created_date = today)
        total = sale.aggregate(cc=Sum('amount'))


    template = 'billing/sales.html'
    context = {
        'sale':sale,
        'total':total,
    }
    return render(request,template,context)


def makepayment(request,pk):
    order = Order.objects.get(id=pk)
    detail = Order_Details.objects.filter(order_id=order.id)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            today = datetime.datetime.now()
            dd = form.cleaned_data['money']
            if order.gross_price > form.cleaned_data['money'] or order.gross_price < form.cleaned_data['money']:
                messages.success(request,"Amount Entered Cannot be less or more  than total transaction")
                return redirect('billing:makepayment',order.id)
            order.money_paid += dd
            tot = detail.aggregate(hq=Sum('hq'),igf=Sum('office'))
            order.save()
            try:
                code = Account_code.objects.get(code="Revenue")
            except Account_code.DoesNotExist:
                code = Account_code.objects.create(code="Revenue")

            Revenue.objects.create(
                account_code=code, amount=dd, hq=tot['hq'], office=tot['igf'],trip = order.trip,order_id = order)
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            SendMessageThread(detail).start()

            messages.success(request, 'Payment made Sucessfully')
            return redirect('billing:manage_orders')
    else:
        form = PaymentForm()
    template = 'billing/check.html'
    context = {
        'order': order,
        'detail': detail,
        'form': form,
    }
    return render(request, template, context)


def correction_state(request):
    if request.session['id']:
        try:
            order =Order.objects.get(id=request.session['id'])
            order.correction = True
            order.save()
            del request.session['id']

            messages.success(request,"Transaction Sent for correction ")
            return redirect('billing:manage_orders')
        except Order.DoesNotExist:
            pass
    else:
        return redirect('billing:manage_orders')


def error_orders(request):

    order = Order.objects.filter(correction=True)

    template = 'billing/search.html'
    Context ={
        'order':order,

    }
    return render(request,template,Context)

def errordeletes_items(request,pk):
    pro = Order_Details.objects.get(id=pk)
    order = Order.objects.get(id=pro.order_id)
    order.gross_price -= pro.unit_price
    order.save()
    pro.delete()
    return redirect('billing:Vew_order',order.id)

def correctiion_order_item(request,pk):
    order = Order.objects.get(id=pk)
    detail = Order_Details.objects.filter(order_id=pk)
    gross_total = detail.aggregate(cc=Sum('unit_price'))
    if request.method == 'POST':
        form = OrderdetailsForm(request.POST)
        if form.is_valid():
            item=form.save(commit=False)
            trip = Trip.objects.get(status = "Active")
            item.order_id=order
            item.unit_price = item.product.unit_price
            item.trip=trip
            item.save()
            order.gross_price+=item.unit_price
            order.save()
            messages.success(request,'Item Added')
            return redirect('billing:correctiion_order_item', order.id)
    else:
        form = OrderdetailsForm()
    template = 'billing/correction_orderitems.html'
    context = {
        'order':order,
        'detail':detail,
        'form':form,
        'gross_total':gross_total,
    }
    return render(request,template,context)

def correction_done(request,pk):
    order = Order.objects.get(id=pk)
    order.correction = False
    order.save()
    messages.success(request,'Correction Done')
    return redirect('billing:Vew_order',order.id)


def correction_checkout(request,pk):

    order = Order.objects.get(id =pk)
    detail = Order_Details.objects.filter(order_id=order.id)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            if order.gross_price > form.cleaned_data['money'] or order.gross_price < form.cleaned_data['money']:
                messages.success(request,"Amount Entered Cannot be less or more  than total transaction")
                return redirect('billing:correction_checkout',order.id)

            else:
                today = datetime.datetime.now()
                order.money_paid += form.cleaned_data['money']
                order.save()
                hq = detail.aggregate(cc=Sum('hq'))
                office = detail.aggregate(cc=Sum('office'))

                try:
                    code = Account_code.objects.get(code="Revenue")
                except Account_code.DoesNotExist:
                    code = Account_code.objects.create(code="Revenue")


                Revenue.objects.create(
                    account_code=code, amount=order.money_paid,hq=hq['cc'],office=office['cc'],trip = order.trip,order_id = order)
                messages.success(request, 'Payment made Sucessfully')
                # SendMessageThread(detail).start()


                return redirect('billing:correction_checkout',order.id)



    else:
        form = PaymentForm()
    template = 'billing/correction_checkout.html'
    context = {
        'order': order,
        'detail': detail,
        'form': form,
    }
    return render(request,template,context)


def delete_revenue(request,pk):
    dd = Revenue.objects.get(id=pk)
    dd.delete()
    messages.success(request,'Record Deleted')
    return redirect('billing:allrevenue')