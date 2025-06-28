from datetime import date

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Client(models.Model):
    phone = PhoneNumberField(
        verbose_name="Телефон",
        region="RU",
    )
    avatar = models.FileField(
        upload_to="media/avatars/",
        null=True,
        blank=True,
    )
    personal_data_consent = models.BooleanField(
        verbose_name="Согласие ОПД",
        default=False
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return f"Клиент с тел: {self.phone}"


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
        upload_to="media/salon_img/",
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
    image = models.ImageField(
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
    services = models.ManyToManyField(
        'Service',
        verbose_name="Оказываемые услуги",
        related_name="masters",
        blank=True,
    )
    salons = models.ManyToManyField(
        'Salon',
        verbose_name="Салоны работы",
        related_name="masters",
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


class Appointment(models.Model):
    PAYMENT_TYPE = (
        ("cash", "Наличностью"),
        ("e_pay", "Электронно"),
    )
    APPOINTMENT_STATUS = (
        ("recorded", "Записан"),
        ("completed", "Выполнен"),
        ("canceled", "Отменен"),
        ("call", "Консультация"),
    )
    APPOINTMENT_TIME = (
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

    # Основная информация о записи
    status = models.CharField(
        verbose_name="Статус записи",
        max_length=20,
        choices=APPOINTMENT_STATUS,
        default="recorded"
    )
    phone = PhoneNumberField(
        verbose_name="Телефон",
        region="RU",
    )
    client_name = models.CharField(
        verbose_name="Имя клиента",
        max_length=100,
        blank=True,
        null=True,
    )
    payment = models.CharField(
        verbose_name='Тип оплаты',
        max_length=15,
        choices=PAYMENT_TYPE,
        default='cash',
        blank=True,
        null=True,
    )
    date = models.DateField(
        verbose_name="Дата записи",
        null=True,
        blank=True,
    )
    time = models.CharField(
        verbose_name="Время записи",
        max_length=20,
        choices=APPOINTMENT_TIME,
        null=True,
        blank=True,
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
    
    # Связи с другими моделями
    client = models.ForeignKey('Client', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Клиент")
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name="appointments",
        verbose_name="Мастер",
        null=True,
        blank=True,
    )
    salon = models.ForeignKey(
        Salon,
        related_name="salon_appointments",
        verbose_name="Салон",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="service_appointments",
        verbose_name="Услуга",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"

    def __str__(self):
        if self.client_name:
            return f"{self.client_name} [{self.phone}]"
        return f"Клиент [{self.phone}]"

    def get_client_name(self):
        """Получить имя клиента из связанного Client или из поля client_name"""
        if self.client and hasattr(self.client, 'user') and self.client.user:
            return self.client.user.first_name or self.client_name
        return self.client_name

    def get_client_phone(self):
        """Получить телефон клиента из связанного Client или из поля phone"""
        if self.client:
            return self.client.phone
        return self.phone

    def save(self, *args, **kwargs):
        """Автоматически связываем с клиентом по телефону при сохранении и проверяем дублирование"""
        # Проверяем дублирование только для новых записей с полными данными
        if not self.pk and self.date and self.time and self.master and self.salon:
            existing = Appointment.objects.filter(
                date=self.date,
                time=self.time,
                master=self.master,
                salon=self.salon,
                status__in=['recorded', 'completed']
            ).exists()
            
            if existing:
                raise ValueError('Мастер уже занят в это время')
        
        # Автоматически связываем с клиентом по телефону
        if self.phone and not self.client:
            try:
                self.client = Client.objects.get(phone=self.phone)
            except Client.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)


class Feedback(models.Model):
    master = models.ForeignKey(
        Master,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name="Мастер",
        null=True,
        blank=True,
    )
    client = models.CharField(
        verbose_name="Кто оставил отзыв",
        max_length=30,
        blank=True,
        null=True
    )
    contact_tel = PhoneNumberField(
        verbose_name="Телефон",
        region="RU",
        blank=True,
        null=True
    )
    comment = models.TextField(
        verbose_name="Отзыв",
        max_length=250,)
    create_at = models.DateField(
        verbose_name="Дата создания",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"Отзыв от {self.client}"
