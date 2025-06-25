from django.contrib import admin
from django.urls import path
from beauty_salon import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('service/', views.service, name='service'),
    path('service-finally/', views.service_finally, name='service_finally'),
    path('notes/', views.notes, name='notes'),
    path('popup/', views.popup, name='popup'),
]
