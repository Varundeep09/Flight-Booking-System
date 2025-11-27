"""
URL configuration for flights frontend pages.
"""
from django.urls import path
from . import views

app_name = 'flights_frontend'

urlpatterns = [
    path('search/', views.search_flights_page, name='search-page'),
    path('results/', views.flight_results_page, name='results-page'),
    path('<int:flight_id>/', views.flight_detail_page, name='detail-page'),
]