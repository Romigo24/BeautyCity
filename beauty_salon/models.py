from datetime import date

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class UserProfile(AbstractUser):
    phone = PhoneNumberField(
        verbose_name="Телефон",
        region="RU",
    )
    avatar = models.ImageField(
        upload_to="static/img/avatars/",
        null=True,
        blank=True,
    )
    personal_data_consent = models.BooleanField(
        verbose_name="Согласие ОПД",
        default=False
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"Пользователь с тел: {self.phone}"


class Service(models.Model):
    name = models.CharField(
        verbose_name="Услуга",
        max_length=50,
    )
    price = models.DecimalField(
        "Цена",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    image = models.FileField(
        upload_to="media/service_img/",
        verbose_name="Картинка",
        blank=True,
    )

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return f"{self.name}"


class Salon(models.Model):
    name = models.CharField(
        "Название салона",
        max_length=50
    )
    address = models.CharField(
        "Адрес",
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        "Контактный телефон",
        max_length=50,
        blank=True,
    )
    image = models.FileField(
        upload_to="media/salon_img/",
        verbose_name="Картинка",
        blank=True,
    )

    class Meta:
        verbose_name = "Салон"
        verbose_name_plural = "Салоны"

    def __str__(self):
        return f"Салон: {self.name} по адресу: {self.address}"


class Master(models.Model):
    name = models.CharField(
        max_length=15,
        verbose_name="Мастер",
    )
    image = models.FileField(
        verbose_name="Картинка",
        upload_to="media/master_img/",
        blank=True,
    )
    specialty = models.CharField(
        max_length=35,
        verbose_name="Специальность",
        blank=True,
    )
    experience_at = models.DateField(
        max_length=35,
        verbose_name="Опыт",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Мастер"
        verbose_name_plural = "Мастера"

    def __str__(self):
        return f"Мастер: {self.name}"

    def get_experience(self):
        if not self.experience_at:
            return "Нет данных"

        delta = date.today() - self.experience_at
        years = delta.days // 365
        months = (delta.days % 365) // 30

        if 11 <= years % 100 <= 14:
            return f"{years} лет, {months}мес."
        elif years % 10 == 1:
            return f"{years} г., {months}мес."
        elif 2 <= years % 10 <= 4:
            return f"{years} г., {months}мес."
        else:
            return f"{years} лет"


class SalonServicePrice(models.Model):
    salon = models.ForeignKey(
        Salon,
        related_name="salons",
        verbose_name="Салон",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="services",
        verbose_name="Услуга",
        null=True,
        blank=True,
    )
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name="masters",
        verbose_name="Мастер",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Услгуга в салоне"
        verbose_name_plural = "Услгуги в салоне"
        unique_together = [
            ["master", "service", "salon"]
        ]

    def __str__(self):
        return f"{self.salon.name} - {self.service.name} - {self.master.name}"


class Order(models.Model):
    PAYMENT_TYPE = (
        ("cash", "Наличностью"),
        ("e_pay", "Электронно"),
    )
    ORDER_STATUS = (
        ("recorded", "Записан"),
        ("completed", "Выполнен"),
        ("canceled", "Отменен"),
        ("call", "Консультация"),
    )
    status = models.CharField(
        verbose_name="Статус записи",
        max_length=20,
        choices=ORDER_STATUS,
        default="recorded"
    )
    phone = PhoneNumberField(
        verbose_name="Телефон",
        region="RU",
    )
    payment = models.CharField(
        verbose_name='Тип оплаты',
        max_length=15,
        choices=PAYMENT_TYPE,
        default='cash',
        blank=True,
        null=True,
    )
    comment = models.TextField(
        verbose_name="Комментарий",
        max_length=250,
        blank=True,
        null=True
    )
    personal_data_consent = models.BooleanField(
        verbose_name="Согласие ОПД",
        default=False
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Пользователь [{self.phone}]"


class OrderService(models.Model):
    ORDER_TIME = (
        ("10:00", "10:00"),
        ("11:00", "11:00"),
        ("12:00", "12:00"),
        ("13:00", "13:00"),
        ("15:00", "15:00"),
        ("16:00", "16:00"),
        ("17:00", "17:00"),
        ("18:00", "18:00"),
        ("19:00", "19:00"),
    )
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name="master_services",
        verbose_name="Мастер",
    )
    salon = models.ForeignKey(
        Salon,
        related_name="salon_services",
        verbose_name="Салон",
        on_delete=models.CASCADE,
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Запись",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="service_items",
        verbose_name="Услуга",
        null=True,
        blank=True,
    )
    record_time_at = models.CharField(
        verbose_name="Время записи",
        max_length=20,
        choices=ORDER_TIME,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "элемент записи"
        verbose_name_plural = "элементы записи"

    def __str__(self):
        return f"{self.master.name}"


class Feedback(models.Model):
    client = models.CharField(
        verbose_name="Кто оставил отзыв",
        max_length=30,
        blank=True,
        null=True
    )
    comment = models.TextField(
        verbose_name="Отзыв",
        max_length=250,)
    create_at = models.DateField(
        verbose_name="Дата создания",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"{self.comment}"
