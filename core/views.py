from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Avg, Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .forms import AppointmentForm, ContactForm, RegistrationForm, ReviewForm
from .models import Appointment, ContactMessage, GalleryImage, Review, Service, TimeSlot


def home(request: HttpRequest) -> HttpResponse:
    services = Service.objects.filter(is_active=True)
    gallery_items = GalleryImage.objects.all()[:8]
    visible_reviews_qs = Review.objects.filter(is_visible=True)
    visible_reviews = visible_reviews_qs.select_related("user")[:10]
    avg_rating = visible_reviews_qs.aggregate(promedio=Avg("rating"))
    contact_form = ContactForm()
    review_form = ReviewForm()

    if request.method == "POST":
        form_type = request.POST.get("form_type")
        if form_type == "contact":
            contact_form = ContactForm(request.POST)
            if contact_form.is_valid():
                contact_form.save()
                messages.success(request, "Gracias por tu mensaje. Te responderemos a la brevedad.")
                return redirect(f"{reverse('core:home')}#contacto")
            messages.error(request, "Por favor revisá los datos del formulario de contacto.")
        elif form_type == "review":
            if not request.user.is_authenticated:
                messages.error(request, "Necesitás iniciar sesión para dejar una valoración.")
                return redirect("login")
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.user = request.user
                review.save()
                messages.success(request, "Gracias por compartir tu experiencia.")
                return redirect(f"{reverse('core:home')}#valoraciones")
            messages.error(request, "No pudimos registrar tu valoración. Revisá los datos ingresados.")

    context = {
        "services": services,
        "gallery": gallery_items,
        "reviews": visible_reviews,
        "avg_rating": avg_rating["promedio"],
        "contact_form": contact_form,
        "review_form": review_form,
    }
    return render(request, "core/home.html", context)


@login_required
def appointment_view(request: HttpRequest) -> HttpResponse:
    today = date.today()
    selected_date_str = request.GET.get("date") or today.isoformat()
    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    except ValueError:
        selected_date = today
    if selected_date < today:
        selected_date = today

    if request.method == "POST":
        selected_date_str = request.POST.get("appointment_date", selected_date_str)
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            selected_date = today
        if selected_date < today:
            selected_date = today

    taken_slots = set(
        Appointment.objects.filter(appointment_date=selected_date).values_list("appointment_time", flat=True)
    )
    all_slots = [choice for choice, _ in TimeSlot.choices]
    available_slots = [slot for slot in all_slots if slot not in taken_slots]

    if request.method == "POST":
        form = AppointmentForm(request.POST, time_choices=available_slots)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            if appointment.appointment_time in taken_slots:
                messages.error(request, "Ese horario ya fue reservado. Elegí otro horario disponible.")
            else:
                try:
                    appointment.deposit_status = Appointment.DepositStatus.PENDING
                    appointment.save()
                except IntegrityError:
                    messages.error(request, "Otro turno se confirmó en ese horario. Elegí una nueva opción disponible.")
                else:
                    messages.success(
                        request,
                        "Tu turno fue reservado. Verificaremos la seña del 50% y te confirmaremos a la brevedad.",
                    )
                    return redirect("core:appointments")
    else:
        initial_data = {
            "appointment_date": selected_date,
        }
        form = AppointmentForm(initial=initial_data, time_choices=available_slots)

    upcoming_appointments = (
        request.user.appointments.filter(appointment_date__gte=today)
        .order_by("appointment_date", "appointment_time")
    )

    services_data = {
        service.pk: {
            "name": service.name,
            "price": format(service.price, ".2f"),
            "deposit": format(
                (service.price * Decimal("0.50")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                ".2f",
            ),
        }
        for service in Service.objects.filter(is_active=True)
    }

    context = {
        "form": form,
        "selected_date": selected_date,
        "taken_slots": sorted(taken_slots),
        "available_slots": available_slots,
        "all_slots": all_slots,
        "upcoming_appointments": upcoming_appointments,
        "today": today,
        "deposit_percentage": 50,
        "services_payment_data": services_data,
    }
    return render(request, "core/appointment.html", context)


def register(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user: User = form.save()
            login(request, user)
            messages.success(request, "Bienvenida/o a Mariana Nails. Tu cuenta fue creada con éxito.")
            return redirect("core:home")
        messages.error(request, "Revisá los datos ingresados para crear la cuenta.")
    else:
        form = RegistrationForm()

    return render(request, "registration/register.html", {"form": form})


@staff_member_required
def admin_dashboard(request: HttpRequest) -> HttpResponse:
    today = date.today()
    week_end = today + timedelta(days=7)

    appointments_today = (
        Appointment.objects.filter(appointment_date=today)
        .select_related("user", "service")
        .order_by("appointment_time")
    )
    upcoming_week = (
        Appointment.objects.filter(appointment_date__gt=today, appointment_date__lte=week_end)
        .select_related("user", "service")
        .order_by("appointment_date", "appointment_time")
    )
    pending_messages_qs = ContactMessage.objects.filter(is_resolved=False)
    pending_messages = pending_messages_qs.order_by("-created_at")[:5]
    recent_reviews = Review.objects.select_related("user").order_by("-created_at")[:5]
    service_summary = (
        Service.objects.annotate(total_appointments=Count("appointments"))
        .order_by("-total_appointments", "name")[:5]
    )

    average_rating = Review.objects.filter(is_visible=True).aggregate(promedio=Avg("rating"))["promedio"]

    pending_deposits = (
        Appointment.objects.filter(deposit_status=Appointment.DepositStatus.PENDING)
        .select_related("user", "service")
        .order_by("appointment_date", "appointment_time")
    )

    stats = {
        "appointments_today": appointments_today.count(),
        "appointments_week": upcoming_week.count(),
        "services_active": Service.objects.filter(is_active=True).count(),
        "pending_messages": pending_messages_qs.count(),
        "average_rating": average_rating,
        "total_clients": User.objects.filter(is_staff=False).count(),
        "pending_deposits": pending_deposits.count(),
    }

    context = {
        "today": today,
        "week_end": week_end,
        "appointments_today": appointments_today,
        "upcoming_week": upcoming_week,
        "pending_messages": pending_messages,
        "recent_reviews": recent_reviews,
        "service_summary": service_summary,
        "stats": stats,
        "pending_deposits": pending_deposits,
    }
    return render(request, "core/dashboard.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def logout_view(request: HttpRequest) -> HttpResponse:
    """End the authenticated session and send the user back home."""
    logout(request)
    messages.success(request, "Cerraste sesión correctamente.")
    return redirect("core:home")


@staff_member_required
@require_http_methods(["POST"])
def verify_deposit(request: HttpRequest, appointment_id: int) -> HttpResponse:
    appointment = get_object_or_404(Appointment.objects.select_related("service", "user"), pk=appointment_id)
    appointment.deposit_status = Appointment.DepositStatus.VERIFIED
    appointment.status = Appointment.STATUS_CONFIRMED
    appointment.deposit_verified_by = request.user
    appointment.deposit_verified_at = timezone.now()
    appointment.save(update_fields=[
        "deposit_status",
        "status",
        "deposit_verified_by",
        "deposit_verified_at",
    ])
    messages.success(
        request,
        f"Se verificó la seña del turno de {appointment.user.get_full_name() or appointment.user.username}.",
    )
    return redirect("core:dashboard")
