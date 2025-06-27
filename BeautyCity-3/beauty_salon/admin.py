from beauty_salon.models import (Feedback, Master, Order, OrderService, Salon,
                                 SalonServicePrice, Service, UserProfile)
from django.contrib import admin
from django.urls import reverse
# from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html


class SalonServicePriceInline(admin.TabularInline):
    model = SalonServicePrice
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderService
    extra = 0


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # list_display = ("username", "phone", "email", "is_staff", "is_superuser")
    # fieldsets = UserAdmin.fieldsets + (
    #     (None, {'fields': ('phone', 'avatar', 'personal_data_consent')}),
    # )
    # add_fieldsets = UserAdmin.add_fieldsets + (
    #     (None, {'fields': ('phone', 'avatar', 'personal_data_consent')}),
    # )
    list_display = ("phone", "get_user_info", "personal_data_consent",)
    list_filter = ("personal_data_consent",)
    search_fields = ("phone", "user__username", "user__first_name", "user__last_name", "user__email")
    # readonly_fields = ("get_user_info_full")
    
    fieldsets = (
        ("Основная информация", {
            "fields": ("phone", "username", "personal_data_consent")
        }),
        ("Дополнительная информация", {
            "fields": ("avatar",),
            "classes": ("collapse",)
        }),
    )

    def get_user_info(self, obj):
        if obj.username:
            return f"{obj.username}"
        return "Не авторизован"
    get_user_info.short_description = "Пользователь"

    def get_user_info_full(self, obj):
        if obj.user:
            return f"""
            Логин: {obj.username}
            Имя: {obj.username.first_name or 'Не указано'}
            Фамилия: {obj.username.last_name or 'Не указано'}
            Email: {obj.username.email or 'Не указан'}
            Дата регистрации: {obj.username.date_joined.strftime('%d.%m.%Y %H:%M')}
            Активен: {'Да' if obj.username.is_active else 'Нет'}
            """
        return "Не авторизован"
    get_user_info_full.short_description = "Информация о пользователе"

    # def get_appointments_count(self, obj):
    #     return obj.appointment_set.count()
    # get_appointments_count.short_description = "Количество записей"

    # def get_last_appointment(self, obj):
    #     last_appointment = obj.order_by('-date', '-time').first()
    #     if last_appointment:
    #         return f"{last_appointment.date} {last_appointment.time}"
    #     return "Нет записей"
    # get_last_appointment.short_description = "Последняя запись"

    # def get_appointments_list(self, obj):
    #     appointments = obj.appointment_set.order_by('-date', '-time')[:10]
    #     if appointments:
    #         html = "<ul>"
    #         for appointment in appointments:
    #             status_color = {
    #                 'recorded': 'blue',
    #                 'completed': 'green', 
    #                 'canceled': 'red',
    #                 'call': 'orange'
    #             }.get(appointment.status, 'black')
    #             html += f"""
    #             <li style="margin-bottom: 10px; padding: 5px; border-left: 3px solid {status_color};">
    #                 <strong>{appointment.date} {appointment.time}</strong><br>
    #                 Мастер: {appointment.master.name if appointment.master else 'Не указан'}<br>
    #                 Услуга: {appointment.service.name if appointment.service else 'Не указана'}<br>
    #                 Салон: {appointment.salon.name if appointment.salon else 'Не указан'}<br>
    #                 Статус: {appointment.get_status_display()}<br>
    #                 Комментарий: {appointment.comment or 'Нет'}
    #             </li>
    #             """
    #         html += "</ul>"
    #         return format_html(html)
    #     return "Нет записей"
    # get_appointments_list.short_description = "История записей"

@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "address",
        "contact_phone",
    )
    search_fields = ['name']
    inlines = [
        SalonServicePriceInline
    ]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )
    search_fields = ['name']
    inlines = [
        SalonServicePriceInline
    ]


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    # list_display = ("name", "get_experience",)
    list_display = ("name", "specialty",)
    search_fields = ("name", "specialty")
    list_filter = ("specialty", "experience_at")
    filter_horizontal = ("services", "salons",)

    # def view_appointments_link(self, obj):
    #     url = reverse('admin:beauty_salon_appointment_changelist') + f'?master__id__exact={obj.id}'
    #     return format_html('<a href="{}">Посмотреть записи</a>', url)
    # view_appointments_link.short_description = "Записи мастера"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # list_display = (
    #     "get_user",
    #     "status",
    #     "comment",
    # )

    # inlines = [OrderItemInline]

    # def get_user(self, obj):
    #     return f'Заказ #{obj.id} {obj.phone}'
    # get_user.short_description = 'Клиент'
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
        return obj.get_client_name()
    get_client_name_display.short_description = "Имя клиента"

    def get_client_phone_display(self, obj):
        return obj.get_client_phone()
    get_client_phone_display.short_description = "Телефон"

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    # list_display = (
    #     "client",
    #     "comment",
    #     "create_at"
    # )
    list_display = ("client", "comment", "create_at")
    list_filter = ("create_at",)
    # search_fields = ("client", "comment")
    readonly_fields = ("create_at",)