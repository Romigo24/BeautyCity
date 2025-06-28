from beauty_salon.models import (Master, Appointment, Salon,
                                 Service, Client, Feedback)
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("phone", "get_user_info", "personal_data_consent",)
    list_filter = ("personal_data_consent",)
    search_fields = ("phone", "user__username", "user__first_name", "user__last_name", "user__email")
    
    fieldsets = (
        ("Основная информация", {
            "fields": ("phone", "user", "personal_data_consent")
        }),
    )

    def get_user_info(self, obj):
        if obj.user:
            return f"{obj.user.username}"
        return "Не авторизован"
    get_user_info.short_description = "Пользователь"


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "address",
        "contact_phone",
    )
    search_fields = ['name', 'address']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
    )
    search_fields = ['name']


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ("name", "specialty", "experience_at")
    search_fields = ("name", "specialty")
    list_filter = ("specialty", "experience_at")
    filter_horizontal = ("services", "salons",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "get_client_name_display",
        "get_client_phone_display", 
        "master",
        "salon", 
        "service", 
        "date",
        "time",
        "status"
    )
    list_filter = ("status", "date", "master", "salon", "service")
    search_fields = ("phone", "client_name", "master__name", "salon__name", "service__name")
    autocomplete_fields = ("master", "salon", "service", "client")

    def get_client_name_display(self, obj):
        if obj.client_name:
            return obj.client_name
        elif obj.client and obj.client.user:
            return obj.client.user.first_name or obj.client.user.username
        return "Не указано"
    get_client_name_display.short_description = "Имя клиента"

    def get_client_phone_display(self, obj):
        return obj.phone
    get_client_phone_display.short_description = "Телефон"


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("client", "master", "comment", "create_at")
    list_filter = ("create_at", "master")
    readonly_fields = ("create_at",)