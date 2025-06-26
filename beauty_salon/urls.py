from beauty_salon.views import (view_call_me, view_index, view_login,
                                view_notes, view_popup, view_register,
                                view_service, view_service_finally)
from django.contrib.auth.views import LogoutView
from django.urls import path

app_name = "beauty_salon"

urlpatterns = [
    path("", view_index, name="index"),
    path("service/", view_service),
    path("service-finally/", view_service_finally, name="service_finally"),
    path("notes/", view_notes, name="notes"),
    path("popup/", view_popup, name="popup"),

    path("register/", view_register, name="register"),
    path("login/", view_login, name="login"),
    path("logout/", LogoutView.as_view(next_page="beauty_salon:index"), name="logout"),
    path("call/", view_call_me, name="call_me"),
]
