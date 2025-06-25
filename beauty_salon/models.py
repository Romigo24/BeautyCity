from django.core.validators import MinValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class UserProfile(models.Model):
    phone = PhoneNumberField(
        verbose_name="Телефон",
        region="RU",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
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
    image = models.ImageField(
        "Картинка",
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
    image = models.ImageField(
        "Картинка",
        blank=True,
    )

    class Meta:
        verbose_name = "Мастер"
        verbose_name_plural = "Мастера"

    def __str__(self):
        return f"Мастер: {self.name}"


class SalonServicePrice(models.Model):
    salon = models.ForeignKey(
        Salon,
        related_name="salons",
        verbose_name="Салон",
        on_delete=models.CASCADE,
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="services",
        verbose_name="Услуга",
    )
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name="masters",
        verbose_name="Мастер",
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
    PAYMENT_TYPE = (
        ("cash", "Наличностью"),
        ("e_pay", "Электронно"),
    )
    ORDER_STATUS = (
        ("recorded", "Записан"),
        ("completed", "Выполнен"),
        ("canceled", "Отменен"),
    )
    status = models.CharField(
        verbose_name="Статус записи",
        max_length=20,
        choices=ORDER_STATUS,
        default="recorded"
    )
    record_time_at = models.DateTimeField(
        verbose_name="Время записи",
        max_length=20,
        choices=ORDER_TIME,
    )
    phone = PhoneNumberField(
        verbose_name="Телефон",
        region="RU",
    )

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Пользователь [{self.phone}] Время: {self.record_time_at} Цена: {self.price_at_order}"


class OrderService(models.Model):
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Услуга",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Запись",
    )

    price = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Цена",
    )

    class Meta:
        verbose_name = "элемент записи"
        verbose_name_plural = "элементы записи"

    def __str__(self):
        return f"{self.master.name} {self.master.price}"