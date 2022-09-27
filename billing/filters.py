import django_filters
from django import forms
from django_filters import DateFilter, CharFilter, NumberFilter
from .models import *


class DateInput(forms.DateInput):
    input_type = 'date'




class RevenueFilter(django_filters.FilterSet):

    start_date = DateFilter(field_name="created_date", lookup_expr='gte', label='Rev Start Date',
                            widget=DateInput(
                                attrs={
                                    'class': 'datepicker'
                                }
                            )

                            )

    end_date = DateFilter(field_name="created_date", lookup_expr='lte', label='Rev End Date',
                          widget=DateInput(
                              attrs={
                                  'class': 'datepicker'
                              }
                          )

                          )

    class Meta:
        model = Revenue
        fields = ['start_date', 'end_date', 'id',
                  'account_code', 'amount','hq', 'office','created_date', 'trip']


class ExpenditureFilter(django_filters.FilterSet):

    start_date = DateFilter(field_name="created_date", lookup_expr='gte', label='Exp Start Date',
                            widget=DateInput(
                                attrs={
                                    'class': 'datepicker'
                                }
                            )

                            )

    end_date = DateFilter(field_name="created_date", lookup_expr='lte', label='Exp End Date',
                          widget=DateInput(
                              attrs={
                                  'class': 'datepicker'
                              }
                          )

                          )

    class Meta:
        model = Expenditure
        fields = ['start_date', 'end_date', 'id',
                  'account_code', 'amount', 'created_date', 'trip']
