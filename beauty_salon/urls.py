from beauty_salon.api import (api_dates, api_masters, api_salons, api_services,
                              api_timeslots)
from beauty_salon.views import (view_call_me, view_feedback, view_index,
                                view_login, view_manager, view_notes,
                                view_register, view_service,
                                view_service_finally)
from django.contrib.auth.views import LogoutView
from django.urls import path

app_name = "beauty_salon"

urlpatterns = [
    path("", view_index, name="index"),
    path("service/", view_service),
    path("service-finally/", view_service_finally, name="service_finally"),
    path("notes/", view_notes, name="notes"),

    path("register/", view_register, name="register"),
    path("login/", view_login, name="login"),
    path("logout/", LogoutView.as_view(next_page="beauty_salon:index"), name="logout"),
    path("call/", view_call_me, name="call_me"),
    path("feedback/", view_feedback, name="feedback"),
    path("manager/", view_manager, name="manager"),

    path('api/salons/', api_salons, name='api_salons'),
    path('api/masters/', api_masters, name='api_masters'),
    path('api/services/', api_services, name='api_services'),
    path('api/timeslots/', api_timeslots, name='api_timeslots'),
    path('api/dates/', api_dates, name='api_dates'),
]
