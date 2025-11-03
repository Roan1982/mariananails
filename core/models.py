from __future__ import annotations

from datetime import time

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = settings.AUTH_USER_MODEL


class TimeSlot(models.TextChoices):
    """Reusable timetable for appointments."""

    H09 = "09:00", "09:00"
    H10 = "10:00", "10:00"
    H11 = "11:00", "11:00"
    H12 = "12:00", "12:00"
    H13 = "13:00", "13:00"
    H14 = "14:00", "14:00"
    H15 = "15:00", "15:00"
    H16 = "16:00", "16:00"
    H17 = "17:00", "17:00"
    H18 = "18:00", "18:00"

    @classmethod
    def to_time(cls, value: str) -> time:
        hour, minute = value.split(":")
        return time(hour=int(hour), minute=int(minute))


class Service(models.Model):
    name = models.CharField("Servicio", max_length=120)
    description = models.TextField("Descripción")
    duration_minutes = models.PositiveIntegerField("Duración (min)", default=60)
    price = models.DecimalField("Precio", max_digits=8, decimal_places=2)
    is_active = models.BooleanField("Disponible", default=True)
    display_order = models.PositiveIntegerField("Orden", default=0)

    class Meta:
        ordering = ["display_order", "name"]
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

    def __str__(self) -> str:
        return self.name


class GalleryImage(models.Model):
    title = models.CharField("Título", max_length=120)
    image = models.ImageField("Imagen", upload_to="gallery/")
    description = models.CharField("Descripción", max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField("Destacado", default=False)

    class Meta:
        ordering = ["-is_featured", "-created_at"]
        verbose_name = "Imagen de galería"
        verbose_name_plural = "Galería"

    def __str__(self) -> str:
        return self.title


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
        "Valoración",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField("Comentario", max_length=800)
    created_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField("Visible", default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Valoración"
        verbose_name_plural = "Valoraciones"

    def __str__(self) -> str:
        return f"{self.user} - {self.rating}"


class ContactMessage(models.Model):
    name = models.CharField("Nombre", max_length=120)
    email = models.EmailField("Email")
    phone = models.CharField("Teléfono", max_length=25, blank=True)
    message = models.TextField("Mensaje", max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField("Respondido", default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Mensaje de contacto"
        verbose_name_plural = "Mensajes de contacto"

    def __str__(self) -> str:
        return f"{self.name} ({self.email})"


class Appointment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendiente"),
        (STATUS_CONFIRMED, "Confirmado"),
        (STATUS_CANCELLED, "Cancelado"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="appointments")
    appointment_date = models.DateField("Fecha")
    appointment_time = models.CharField("Horario", choices=TimeSlot.choices, max_length=5)
    notes = models.CharField("Notas", max_length=255, blank=True)
    status = models.CharField("Estado", max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["appointment_date", "appointment_time"]
        unique_together = ("appointment_date", "appointment_time")
        verbose_name = "Turno"
        verbose_name_plural = "Turnos"

    def __str__(self) -> str:
        return f"{self.service} - {self.appointment_date} {self.appointment_time}"

    @property
    def appointment_datetime(self):
        return self.appointment_date, TimeSlot.to_time(self.appointment_time)
