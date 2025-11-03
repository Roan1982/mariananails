from __future__ import annotations

from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase

from .forms import AppointmentForm
from .models import Service, TimeSlot


class AppointmentFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="secret123")
        self.service = Service.objects.create(
            name="Manicuría clásica",
            description="Corte, limado y esmaltado",
            duration_minutes=60,
            price=3000,
        )

    def test_prevents_past_dates(self):
        yesterday = date.today() - timedelta(days=1)
        form = AppointmentForm(
            data={
                "service": self.service.pk,
                "appointment_date": yesterday,
                "appointment_time": TimeSlot.H10,
                "notes": "",
            },
            time_choices=[choice for choice, _ in TimeSlot.choices],
        )
        self.assertFalse(form.is_valid())
        self.assertIn("No podés reservar un turno en el pasado.", form.errors["appointment_date"])
