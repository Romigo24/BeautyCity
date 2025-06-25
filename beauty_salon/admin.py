from beauty_salon.models import (Master, Order, OrderService, Salon,
                                 SalonServicePrice, Service, UserProfile)
from django.contrib import admin


class SalonServicePriceInline(admin.TabularInline):
    model = SalonServicePrice
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderService
    extra = 0


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('phone', )


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        SalonServicePriceInline
    ]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        'name',
    ]
    inlines = [
        SalonServicePriceInline
    ]


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'phone',
        'status',
        'record_time_at',
    )

    inlines = [OrderItemInline]