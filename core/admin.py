from __future__ import annotations

from django.contrib import admin

from .models import Appointment, ContactMessage, GalleryImage, Review, Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "duration_minutes", "is_active")
    list_editable = ("price", "duration_minutes", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("display_order", "name")


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("title", "is_featured", "created_at")
    list_filter = ("is_featured",)
    search_fields = ("title", "description")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("user", "rating", "created_at", "is_visible")
    list_filter = ("rating", "is_visible")
    search_fields = ("user__username", "comment")
    autocomplete_fields = ("user",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at", "is_resolved")
    list_filter = ("is_resolved", "created_at")
    search_fields = ("name", "email", "message")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "service",
        "user",
        "appointment_date",
        "appointment_time",
        "status",
        "created_at",
    )
    list_filter = ("status", "appointment_date", "service")
    search_fields = ("user__username", "service__name")
    autocomplete_fields = ("service", "user")
    ordering = ("-appointment_date", "appointment_time")
