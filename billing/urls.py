from billing.models import Trip
from django.urls import path
from .import views
from .import services
from .import trip
from .import cashier
from .import management



app_name = 'billing'

urlpatterns = [

    #products
    path('create_category',services.create_category, name='create_category'),
    path('manage_category',services.manage_category,name='manage_category'),
    path('edit_category/<str:pk>/',services.edit_category,name='edit_category'),
    path('manage_product',services.manage_product,name='manage_product'),
    path('create_product',services.create_product,name='create_product'),
    path('edit_product/<str:pk>/',services.edit_product,name='edit_product'),

    #trips
    path('create_trip',trip.create_trip,name='create_trip'),
    path('manage_trip',trip.manage_trip,name='manage_trip'),


    #orders
    path('create_customer',cashier.create_customer,name='create_customer'),
    path('orderitems',cashier.orderitems.as_view(),name='orderitems'),
    path('deletes_items/<str:pk>/',cashier.deletes_items,name='deletes_items'),
    path('checkout',cashier.checkout,name='checkout'),
    path('manage_orders',cashier.manage_orders,name='manage_orders'),
    path('closed',cashier.closed,name='closed'),
    path('close',cashier.close,name='close'),
    path('Vew_order/<str:pk>/',cashier.Vew_order,name='Vew_order'),
    path('makepayment/<str:pk>/',cashier.makepayment,name='makepayment'),
    path('search_orders',cashier.search_orders,name='search_orders'),
    path('correction_state',cashier.correction_state,name='correction_state'),
    path('error_orders',cashier.error_orders,name='error_orders'),
    path('errordeletes_items/<str:pk>/',cashier.errordeletes_items,name='errordeletes_items'),
    path('correctiion_order_item/<str:pk>/',cashier.correctiion_order_item,name='correctiion_order_item'),
    path('correction_done/<str:pk>/',cashier.correction_done,name='correction_done'),
    path('correction_checkout/<str:pk>/',cashier.correction_checkout,name='correction_checkout'),

    #Account
    path('allrevenue',cashier.allrevenue,name='allrevenue'),
    path('allexpenses',cashier.allexpenses,name='allexpenses'),
    path('income_expenditure',cashier.income_expenditure,name='income_expenditure'),
    path('daily_sales',cashier.daily_sales,name='daily_sales'),

    #Pv
    path('manage_pv',cashier.manage_pv,name='manage_pv'),
    path('create_pv',cashier.create_pv,name='create_pv'),
    path('pv_detail',cashier.pv_detail.as_view(),name='pv_detail'),
    path('deletes_pvitems',cashier.deletes_pvitems,name='deletes_pvitems'),
    path('closepv',cashier.closepv,name='closepv'),
    path('pending_pv',cashier.pending_pv,name='pending_pv'),
    path('deletes_pvitems/<str:pk>/',cashier.deletes_pvitems,name='deletes_pvitems'),
    path('View_pv/<str:pk>/',cashier.View_pv,name='View_pv'),
    path('pending_pv',cashier.pending_pv,name='pending_pv'),
    path('cancelled/<str:pk>/',cashier.cancelled,name='cancelled'),
    path('approve/<str:pk>/',cashier.approve,name='approve'),
    path('delete_revenue/<str:pk>/',cashier.delete_revenue,name='delete_revenue'),

    #manager
    path('managerdashboard',management.managerdashboard,name='managerdashboard'),



]