from __future__ import annotations

from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("reservas/", views.appointment_view, name="appointments"),
    path("registro/", views.register, name="register"),
    path("gestion/", views.admin_dashboard, name="dashboard"),
]
