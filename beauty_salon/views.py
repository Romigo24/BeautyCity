from beauty_salon.models import Feedback, Master, Order, Salon, Service
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterUser


def view_index(request):
    if request.method == "POST":
        contact_name = request.POST.get('fname')
        contact_tel = request.POST.get('tel')
        question = request.POST.get('contactsTextarea')
        personal_data_consent = bool(request.POST.get('checkbox'))

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
    if request.method == "POST":
        contact_tel = request.POST.get('tel')
        personal_data_consent = bool(request.POST.get('checkbox'))

        Order.objects.create(
            status="call",
            phone=contact_tel,
            personal_data_consent=personal_data_consent,
            comment="Перезвонить"
        )
        messages.success(request, 'Спасибо, мы вам перезвоним в течение часа.')
        return redirect("beauty_salon:index")

    return render(request, "call_me.html")


def view_service(request):
    return render(request, "service.html")


def view_service_finally(request):
    return render(request, "serviceFinally.html")


@login_required(login_url="beauty_salon:login")
def view_notes(request):
    return render(request, "notes.html")


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
