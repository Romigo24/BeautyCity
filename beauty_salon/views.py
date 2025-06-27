from datetime import date, datetime

from beauty_salon.models import (Feedback, Master, Order, Salon, Service,
                                 UserProfile)
from beauty_salon.utils import validate_phone
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, RegisterUser


def view_index(request):
    if request.method == "POST":
        contact_name = request.POST.get("fname")
        contact_tel = request.POST.get("tel")
        question = request.POST.get("contactsTextarea")
        personal_data_consent = bool(request.POST.get("checkbox"))

        Order.objects.create(
            status="call",
            phone=contact_tel,
            personal_data_consent=personal_data_consent,
            comment=f"От {contact_name}\nВопрос: {question}"
        )

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


def view_call_me(request):
    errors = {}
    if request.method == "POST":
        contact_tel = request.POST.get("tel")
        personal_data_consent = bool(request.POST.get("checkbox"))

        if not validate_phone(contact_tel):
            errors["contact_tel"] = ["Введен некорректный номер телефона."]
        if errors:
            return render(request, "call_me.html", {"errors": errors})
        try:
            Order.objects.create(
                status="call",
                phone=contact_tel,
                personal_data_consent=personal_data_consent,
                comment="Перезвонить"
            )
            messages.success(request, "Спасибо, мы вам перезвоним в течение часа.")
            return redirect("beauty_salon:index")

        except ValidationError as e:
            errors = e.message_dict if hasattr(e, "message_dict") else {"error": e.messages}
            return render(request, "call_me.html", {"errors": errors})

    return render(request, "call_me.html")


def view_service(request):
    salons = Salon.objects.order_by("name")
    return render(
        request, 
        "service.html", {"salons": salons,}
        )


def view_service_finally(request):
    if request.method == "POST":
        # Получаем данные из формы
        phone = request.POST.get("tel")
        name = request.POST.get("fname")
        salon_id = request.POST.get("salon")
        master_id = request.POST.get("master")
        service_id = request.POST.get("service")
        date_str = request.POST.get("date")
        time = request.POST.get("time")
        
        # Преобразуем строку даты в объект date
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            messages.error(request, "Неверный формат даты!")
            return render(request, "serviceFinally.html", {"error": True})
        
        # Проверяем, не существует ли уже запись с такими же параметрами
        # Мастер не может работать одновременно с разными сервисами в одно время
        existing_appointment = Order.objects.filter(
            date=date_obj,
            time=time,
            master_id=master_id,
            salon_id=salon_id,
            status__in=["recorded", "completed"]
        ).first()
        
        if existing_appointment:
            messages.error(request, f"Запись на это время уже существует! Мастер {existing_appointment.master.name} уже занят в {time} на {date_obj}.")
            return render(request, "serviceFinally.html", {"error": True})
        
        # Если пользователь авторизован, ищем клиента по пользователю
        if request.user.is_authenticated:
            try:
                client = UserProfile.objects.get(user=request.user)
                # Обновляем телефон, если он изменился
                if client.phone != phone:
                    client.phone = phone
                # Обновляем имя, если оно не указано в форме
                if not name and hasattr(request.user, "first_name") and request.user.first_name:
                    name = request.user.first_name
                client.personal_data_consent = True
                client.save()
            except UserProfile.DoesNotExist:
                # Создаем нового клиента для авторизованного пользователя
                client = UserProfile.objects.create(
                    phone=phone,
                    user=request.user,
                    personal_data_consent=True
                )
        else:
            # Для неавторизованных пользователей ищем по телефону
            client, _ = UserProfile.objects.get_or_create(phone=phone)
            client.personal_data_consent = True
            client.save()
        
        # Создаём запись
        try:
            Order.objects.create(
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
            messages.success(request, "Запись успешно создана!")
            return render(request, "serviceFinally.html", {"success": True})
        except ValueError as e:
            if "Мастер уже занят в это время" in str(e):
                messages.error(request, "Мастер уже занят в это время!")
            else:
                messages.error(request, "Ошибка при создании записи!")
            return render(request, "serviceFinally.html", {"error": True})
    else:
        # GET: показываем детали выбранной записи
        salon_id = request.GET.get("salon")
        master_id = request.GET.get("master")
        service_id = request.GET.get("service")
        date = request.GET.get("date")
        time = request.GET.get("time")
        context = {}
        if salon_id:
            context["salon"] = get_object_or_404(Salon, id=salon_id)
        if master_id:
            context["master"] = get_object_or_404(Master, id=master_id)
        if service_id:
            context["service"] = get_object_or_404(Service, id=service_id)
        context["date"] = date
        context["time"] = time
        return render(request, "serviceFinally.html", context)


@login_required(login_url="beauty_salon:login")
def view_feedback(request):
    errors = {}
    data = {}
    if request.method == "POST":
        contact_name = request.POST.get("fname")
        contact_tel = request.POST.get("tel")
        visit_date = request.POST.get("dateVis")
        text = request.POST.get("popupTextarea")
        data = {
            "client": contact_name,
            "contact_tel": contact_tel,
            "create_at": visit_date,
            "comment": text,
        }
        if not validate_phone(contact_tel):
            errors["contact_tel"] = ["Введен некорректный номер телефона."]
        if errors:
            return render(request, "feedback.html", {"errors": errors, "data": data})

        try:
            Feedback.objects.create(
                client=contact_name,
                contact_tel=contact_tel,
                comment=text,
                create_at=visit_date,
            )
            return render(request, "index.html", {"success": True})
        except ValidationError as e:
            errors = e.message_dict if hasattr(e, "message_dict") else {"error": e.messages}
            return render(request, "feedback.html", {"errors": errors, "data": data})

    return render(request, "feedback.html")


@login_required(login_url="beauty_salon:login")
def view_notes(request):
    if not request.user.is_authenticated:
        return render(
            request,
            "notes.html",
            {"upcoming_appointments": [], "past_appointments": []}
        )

    today = date.today()

    upcoming_appointments = Order.objects.filter(
        client=request.user,
        date__gte=today,
        status__in=["recorded"]
    ).order_by("date", "time")

    past_appointments = Order.objects.filter(
        client=request.user,
        date__lt=today,
        status__in=["completed", "canceled"]
    ).order_by("-date", "-time")

    return render(request, "notes.html", {
        "upcoming_appointments": upcoming_appointments,
        "past_appointments": past_appointments,
    })


def view_popup(request):
    return render(request, "popup.html")


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
