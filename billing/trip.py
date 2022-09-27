from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.contrib import messages
import datetime


def create_trip(request):
    try:
        cc= Trip.objects.all().order_by('id')
        if cc:
            trip = cc.reverse()[0]
            trip.status = "Inactive"
            trip.save()
        else:
            cc = None
    except Trip.DoesNotExist:
        pass
    today = datetime.datetime.now()
    Trip.objects.create(status = "Active",trip_date=today)

    messages.success(request, "Trip Created")
    return redirect('billing:manage_trip')


def manage_trip(request):
    trips = Trip.objects.all()
    template = 'billing/manage_trip.html'
    context={
        'trips':trips,
    }
    return render(request,template,context)

