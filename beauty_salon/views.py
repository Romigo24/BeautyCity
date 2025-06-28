from datetime import date, datetime
import json
from beauty_salon.utils import get_month_info

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from yookassa import Configuration, Payment
from .forms import LoginForm, RegisterUser
from .models import Appointment, Client, Feedback, Master, Salon, Service
from .utils import validate_phone



Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def create_payment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    payment = Payment.create({
        "amount": {
            "value": str(appointment.service.price),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": request.build_absolute_uri(
                reverse('beauty_salon:notes') + f'?appointment_id={appointment.id}'
            )
        },
        "capture": True,
        "description": f"Оплата услуги: {appointment.service.name}",
        "metadata": {
            "appointment_id": appointment.id
        }
    })

    appointment.yookassa_payment_id = payment.id
    appointment.payment_status = 'waiting'
    appointment.save()

    return redirect(payment.confirmation.confirmation_url)

def payment_success(request):
    payment_id = request.GET.get('payment_id')
    if payment_id:
        try:
            payment = Payment.find_one(payment_id)
            if payment.status == 'succeeded':
                appointment = Appointment.objects.get(yookassa_payment_id=payment_id)
                appointment.payment_status = 'paid'
                appointment.payment_date = timezone.now()
                appointment.save()
                messages.success(request, 'Оплата прошла успешно!')
        except Exception:
            pass

    return redirect('beauty_salon:notes')

def payment_fail(request):
    payment_id = request.GET.get('payment_id')
    if payment_id:
        try:
            appointment = Appointment.objects.get(yookassa_payment_id=payment_id)
            appointment.payment_status = 'failed'
            appointment.save()
            messages.error(request, 'Оплата не была завершена')
        except Exception:
            pass

    return redirect('beauty_salon:notes')

@csrf_exempt
def yookassa_webhook(request):
    if request.method == 'POST':
        event_json = json.loads(request.body)
        payment_id = event_json['object']['id']

        try:
            appointment = Appointment.objects.get(yookassa_payment_id=payment_id)
            payment = Payment.find_one(payment_id)

            if payment.status == 'succeeded':
                appointment.payment_status = 'paid'
                appointment.payment_date = timezone.now()
                appointment.save()

        except Exception:
            pass

    return HttpResponse(status=200)

def index(request):
    if request.method == "POST":
        contact_name = request.POST.get("fname")
        contact_tel = request.POST.get("tel")
        question = request.POST.get("contactsTextarea")
        personal_data_consent = bool(request.POST.get("checkbox"))

        Appointment.objects.create(
            status="call",
            phone=contact_tel,
            client_name=contact_name,
            personal_data_consent=personal_data_consent,
            comment=f"Вопрос: {question}" if question else "Консультация"
        )
        messages.success(request, 'Спасибо за обращение! Мы свяжемся с вами в ближайшее время.')

    salons = Salon.objects.order_by("name")
    services = Service.objects.all()
    masters = Master.objects.all()
    feedbacks = Feedback.objects.all()
    return render(
        request,
        "index.html",
        {
            "salons": salons,
            "services": services,
            "masters": masters,
            "feedbacks": feedbacks,
        }
    )


def service(request):
    salons = Salon.objects.order_by("name")
    return render(request, 'service.html', {"salons": salons})


def service_finally(request):
    if request.method == 'POST':
        # Получаем данные из формы
        phone = request.POST.get('tel')
        name = request.POST.get('fname')
        salon_id = request.POST.get('salon')
        master_id = request.POST.get('master')
        service_id = request.POST.get('service')
        date_str = request.POST.get('date')
        time = request.POST.get('time')
        
        # Преобразуем строку даты в объект date
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, 'Неверный формат даты!')
            return render(request, 'serviceFinally.html', {'error': True})
        
        # Проверяем, не существует ли уже запись с такими же параметрами
        # Мастер не может работать одновременно с разными сервисами в одно время
        existing_appointment = Appointment.objects.filter(
            date=date_obj,
            time=time,
            master_id=master_id,
            salon_id=salon_id,
            status__in=['recorded', 'completed']
        ).first()
        
        if existing_appointment:
            messages.error(request, f'Запись на это время уже существует! Мастер {existing_appointment.master.name} уже занят в {time} на {date_obj}.')
            return render(request, 'serviceFinally.html', {'error': True})
        
        # Если пользователь авторизован, ищем клиента по пользователю
        if request.user.is_authenticated:
            try:
                client = Client.objects.get(user=request.user)
                # Обновляем телефон, если он изменился
                if client.phone != phone:
                    client.phone = phone
                # Обновляем имя, если оно не указано в форме
                if not name and hasattr(request.user, 'first_name') and request.user.first_name:
                    name = request.user.first_name
                client.personal_data_consent = True
                client.save()
            except Client.DoesNotExist:
                # Создаем нового клиента для авторизованного пользователя
                client = Client.objects.create(
                    phone=phone,
                    user=request.user,
                    personal_data_consent=True
                )
        else:
            # Для неавторизованных пользователей ищем по телефону
            client, _ = Client.objects.get_or_create(phone=phone)
            client.personal_data_consent = True
            client.save()
        
        # Создаём запись
        try:
            appointment = Appointment.objects.create(
                phone=phone,
                client_name=name,
                date=date_obj,
                time=time,
                client=client,
                master_id=master_id,
                salon_id=salon_id,
                service_id=service_id,
                personal_data_consent=True
            )
            messages.success(request, 'Запись успешно создана!')
            return render(request, 'serviceFinally.html', {'success': True})
        except ValueError as e:
            if 'Мастер уже занят в это время' in str(e):
                messages.error(request, 'Мастер уже занят в это время!')
            else:
                messages.error(request, 'Ошибка при создании записи!')
            return render(request, 'serviceFinally.html', {'error': True})
    else:
        # GET: показываем детали выбранной записи
        salon_id = request.GET.get('salon')
        master_id = request.GET.get('master')
        service_id = request.GET.get('service')
        date = request.GET.get('date')
        time = request.GET.get('time')
        context = {}
        if salon_id:
            context['salon'] = get_object_or_404(Salon, id=salon_id)
        if master_id:
            context['master'] = get_object_or_404(Master, id=master_id)
        if service_id:
            context['service'] = get_object_or_404(Service, id=service_id)
        context['date'] = date
        context['time'] = time
        return render(request, 'serviceFinally.html', context)


@login_required
def notes(request):
    # Обработка статуса оплаты
    payment_id = request.GET.get('payment_id')
    appointment_id = request.GET.get('appointment_id')

    if payment_id or appointment_id:
        try:
            if payment_id:
                appointment = Appointment.objects.get(
                    yookassa_payment_id=payment_id,
                    client__user=request.user
                )
            else:
                appointment = Appointment.objects.get(
                    id=appointment_id,
                    client__user=request.user
                )

            if appointment.yookassa_payment_id:
                payment = Payment.find_one(appointment.yookassa_payment_id)
                if payment.status == 'succeeded' and appointment.payment_status != 'paid':
                    appointment.payment_status = 'paid'
                    appointment.payment_date = timezone.now()
                    appointment.save()
                    messages.success(request, 'Оплата прошла успешно!')
                elif payment.status == 'canceled' and appointment.payment_status != 'failed':
                    appointment.payment_status = 'failed'
                    appointment.save()
                    messages.error(request, 'Платеж был отменен')
        except Appointment.DoesNotExist:
            messages.error(request, 'Запись не найдена')
        except Exception:
            messages.error(request, 'Ошибка при проверке статуса платежа')

    try:
        client = Client.objects.get(user=request.user)

        today = date.today()
        upcoming_appointments = Appointment.objects.filter(
            client=client,
            date__gte=today,
            status__in=['recorded']
        ).order_by('date', 'time')

        past_appointments = Appointment.objects.filter(
            client=client, 
            date__lt=today, 
            status__in=['completed', 'canceled']
        ).order_by('-date', '-time')

    except Client.DoesNotExist:
        upcoming_appointments = []
        past_appointments = []

    return render(request, 'notes.html', {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'is_manager': request.user.is_staff,
    })


def popup(request):
    return render(request, 'popup.html')


def view_call_me(request):
    errors = {}
    if request.method == "POST":
        contact_tel = request.POST.get('tel')
        personal_data_consent = bool(request.POST.get('checkbox'))

        if not validate_phone(contact_tel):
            errors["contact_tel"] = ["Введен некорректный номер телефона."]
        if errors:
            return render(request, "call_me.html", {"errors": errors})

        Appointment.objects.create(
            status="call",
            phone=contact_tel,
            personal_data_consent=personal_data_consent,
            comment="Перезвонить"
        )
        messages.success(request, 'Спасибо, мы вам перезвоним в течение часа.')
        return redirect("beauty_salon:index")

    return render(request, "call_me.html")


def view_register(request):
    if request.method == "POST":
        form = RegisterUser(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("beauty_salon:index")
    else:
        form = RegisterUser()
    return render(request, "register.html", {"form": form})


def view_login(request):
    form = LoginForm(data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("beauty_salon:index")
    return render(request, "login.html", {"form": form})


@login_required(login_url="beauty_salon:login")
def view_feedback(request):
    errors = {}
    data = {}
    masters = Master.objects.all()
    if request.method == "GET":
        master_id = request.GET.get("master_id")
        if master_id:
            data["master_id"] = master_id

    if request.method == "POST":
        contact_name = request.POST.get("fname")
        contact_tel = request.POST.get("tel")
        visit_date = request.POST.get("dateVis")
        text = request.POST.get("popupTextarea")
        master_id = request.POST.get("master_id")

        data = {
            "client": contact_name,
            "contact_tel": contact_tel,
            "create_at": visit_date,
            "comment": text,
            "master_id": master_id,
        }
        try:
            master = Master.objects.get(id=master_id)
        except (Master.DoesNotExist, ValueError, TypeError):
            master = None
            errors["master"] = ["Выберите мастера."]

        if not validate_phone(contact_tel):
            errors["contact_tel"] = ["Введен некорректный номер телефона."]
        if errors:
            return render(request, "feedback.html", {"errors": errors, "data": data, "masters": masters})

        try:
            Feedback.objects.create(
                master=master,
                client=contact_name,
                contact_tel=contact_tel,
                comment=text,
                create_at=visit_date,
            )
            return redirect("beauty_salon:notes")
        except ValidationError as e:
            errors = e.message_dict if hasattr(e, "message_dict") else {"error": e.messages}
            return render(request, "feedback.html", {"errors": errors, "data": data, "masters": masters})

    return render(request, "feedback.html", {"masters": masters, "data": data})


def is_manager(user):
    return user.is_authenticated and user.is_staff


@login_required(login_url="beauty_salon:login")
@user_passes_test(is_manager, login_url="beauty_salon:login")
def view_manager(request):
    month_info = get_month_info()

    data_current_month = Appointment.objects.select_related(
        "client", "master", "salon", "service"
    ).filter(
        date__gte=month_info["first_day"],
        date__lt=month_info["first_day_next"],
        date__year=month_info["year"]
    )

    visits_this_year = Appointment.objects.filter(date__year=month_info["year"]).count()
    visits_month = data_current_month.count()
    paid_count = data_current_month.filter(status="completed").count()
    percent_paid = (paid_count / visits_month) * 100 if visits_month else 0
    total_payment_current_month = sum(order.service.price for order in data_current_month.filter(status="completed") if order.service)
    percent_visits = (visits_month / visits_this_year) * 100 if visits_this_year else 0

    return render(
        request,
        "manager.html",
        {
            "current_month": month_info["month_name"],
            "total_payment_current_month": total_payment_current_month,
            "visits_month": visits_month,
            "percent_visits": percent_visits,
            "visits_this_year": visits_this_year,
            "paid_count": paid_count,
            "percent_paid": percent_paid,
        }
    )


def privacy_policy(request):
    """Отображение политики конфиденциальности"""
    return render(request, 'privacy_policy.html')
