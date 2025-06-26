from beauty_salon.models import (Feedback, Master, Order, OrderService, Salon,
                                 SalonServicePrice, Service, UserProfile)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


class SalonServicePriceInline(admin.TabularInline):
    model = SalonServicePrice
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderService
    extra = 0


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("username", "phone", "email", "is_staff", "is_superuser")
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone', 'avatar', 'personal_data_consent')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone', 'avatar', 'personal_data_consent')}),
    )


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "address",
        "contact_phone",
    )
    inlines = [
        SalonServicePriceInline
    ]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )
    inlines = [
        SalonServicePriceInline
    ]


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ("name", "get_experience",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "get_user",
        "status",
        "comment",
    )

    inlines = [OrderItemInline]

    def get_user(self, obj):
        return f'Заказ #{obj.id} {obj.phone}'
    get_user.short_description = 'Клиент'


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "client",
        "comment",
        "create_at"
    )
