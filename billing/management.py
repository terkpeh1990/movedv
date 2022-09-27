from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage  # To upload Profile Picture
from django.urls import reverse
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .forms import *
from .models import *


def managerdashboard(request):
    try:
        trip = Trip.objects.get(status= "Active")
        attendance = Order.objects.filter(trip=trip.id,gross_price__gt=0.00).count()
        revenue = Revenue.objects.filter(trip=trip.id)
        expense= Expenditure.objects.filter(trip=trip.id)
        trip_revenue =revenue.aggregate(cc =Sum('amount'),hq=Sum('hq'), igf=Sum('office'))
        trip_expense = expense.aggregate(cc =Sum('amount'))
        today = datetime.datetime.now()
        total_revenue = trip_revenue
        total_expenditure = trip_expense
        


        pending_pv = Pv.objects.filter(trip=trip.id,status="Pending")
        approved_pv = Pv.objects.filter(trip=trip.id, status="Approved")
        total_pending = pending_pv.aggregate(cc=Sum('amount'))
        total_approved = approved_pv.aggregate(cc=Sum('amount'))
    except Trip.DoesNotExist:
        # trip = Trip.objects.get(status= "Active")
        attendance = Order.objects.filter(gross_price__gt=0.00).count()
        revenue = Revenue.objects.all()
        expense= Expenditure.objects.all()
        trip_revenue =revenue.aggregate(cc =Sum('amount'),hq=Sum('hq'), igf=Sum('office'))
        trip_expense = expense.aggregate(cc =Sum('amount'))
        today = datetime.datetime.now()
        total_revenue = trip_revenue
        total_expenditure = trip_expense
        


        pending_pv = Pv.objects.filter(status="Pending")
        approved_pv = Pv.objects.filter( status="Approved")
        total_pending = pending_pv.aggregate(cc=Sum('amount'))
        total_approved = approved_pv.aggregate(cc=Sum('amount'))


    if total_revenue['cc'] and not total_expenditure['cc']:
        expected_cash = total_revenue['cc']
    elif not total_revenue['cc'] and total_expenditure['cc']:
        expected_cash = -total_expenditure['cc']
    elif not total_revenue['cc'] and not total_expenditure['cc']:
        expected_cash = 0.00
    else:
        expected_cash = total_revenue['cc'] - \
            total_expenditure['cc']
    context ={
        
        'total_revenue': total_revenue,
        'total_expenditure': total_expenditure,
        'expected_cash': expected_cash,
        
        'pending_pv': pending_pv,
        'approved_pv': approved_pv,
        'total_pending': total_pending,
        'total_approved': total_approved,
        'attendance':attendance,
        


    }

    template='billing/manager.html'
    return render(request,template,context)

