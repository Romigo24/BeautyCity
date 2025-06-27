from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from beauty_salon import views
from beauty_salon.api import api_salons, api_masters, api_services, api_timeslots, api_dates

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('service/', views.service, name='service'),
    path('service-finally/', views.service_finally, name='service_finally'),
    path('notes/', views.notes, name='notes'),
    path('popup/', views.popup, name='popup'),
    
    # Новые маршруты для аутентификации
    path('register/', views.view_register, name='register'),
    path('login/', views.view_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('call/', views.view_call_me, name='call_me'),
    
    # API endpoints
    path('api/salons/', api_salons, name='api_salons'),
    path('api/masters/', api_masters, name='api_masters'),
    path('api/services/', api_services, name='api_services'),
    path('api/timeslots/', api_timeslots, name='api_timeslots'),
    path('api/dates/', api_dates, name='api_dates'),
]
