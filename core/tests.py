from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.models import User
from django.test import TestCase

from .forms import AppointmentForm
from .models import Appointment, Service, TimeSlot


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
                "payment_method": Appointment.PaymentMethod.TRANSFER,
                "payment_reference": "REF123",
                "notes": "",
            },
            time_choices=[choice for choice, _ in TimeSlot.choices],
        )
        self.assertFalse(form.is_valid())
        self.assertIn("No podés reservar un turno en el pasado.", form.errors["appointment_date"])

    def test_requires_payment_reference(self):
        tomorrow = date.today() + timedelta(days=1)
        form = AppointmentForm(
            data={
                "service": self.service.pk,
                "appointment_date": tomorrow,
                "appointment_time": TimeSlot.H11,
                "payment_method": Appointment.PaymentMethod.TRANSFER,
                "payment_reference": "   ",
                "notes": "",
            },
            time_choices=[choice for choice, _ in TimeSlot.choices],
        )
        self.assertFalse(form.is_valid())
        self.assertIn("Necesitamos un comprobante", form.errors["payment_reference"][0])

    def test_deposit_amount_is_half_service_price(self):
        tomorrow = date.today() + timedelta(days=1)
        form = AppointmentForm(
            data={
                "service": self.service.pk,
                "appointment_date": tomorrow,
                "appointment_time": TimeSlot.H12,
                "payment_method": Appointment.PaymentMethod.MERCADOPAGO,
                "payment_reference": "MP-12345",
                "notes": "",
            },
            time_choices=[choice for choice, _ in TimeSlot.choices],
        )
        self.assertTrue(form.is_valid(), form.errors)
        appointment = form.save(commit=False)
        appointment.user = self.user
        appointment.save()
        expected = (self.service.price * Decimal("0.50")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.assertEqual(appointment.deposit_amount, expected)
