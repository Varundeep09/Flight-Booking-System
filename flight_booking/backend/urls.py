"""
URL configuration for flight_booking project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/flights/', include('flights.urls')),
    path('api/bookings/', include('bookings.urls')),
    
    # Frontend URLs
    path('', TemplateView.as_view(template_name='flights/search.html'), name='home'),
    path('flights/', include('flights.frontend_urls')),
    path('bookings/', include('bookings.frontend_urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)