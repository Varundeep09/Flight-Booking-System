"""
URL configuration for flights API endpoints.
"""
from django.urls import path
from . import views

app_name = 'flights'

urlpatterns = [
    # API endpoints
    path('search/', views.FlightSearchView.as_view(), name='flight-search'),
    path('<int:id>/', views.FlightDetailView.as_view(), name='flight-detail'),
    path('airlines/', views.AirlineListView.as_view(), name='airline-list'),
    path('airports/', views.AirportListView.as_view(), name='airport-list'),
    path('fare-history/', views.FareHistoryView.as_view(), name='fare-history'),
    path('validate-search/', views.validate_search, name='validate-search'),
    path('analytics/', views.flight_analytics, name='flight-analytics'),
]