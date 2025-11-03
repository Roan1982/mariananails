from __future__ import annotations

from datetime import date, datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Appointment, ContactMessage, Review, Service, TimeSlot


class ContactForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 4, "placeholder": "Contanos cómo podemos ayudarte"}),
        }


class ReviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.NumberInput(attrs={"min": 1, "max": 5}),
            "comment": forms.Textarea(attrs={"rows": 3, "placeholder": "¿Cómo fue tu experiencia?"}),
        }


class AppointmentForm(forms.ModelForm):
    appointment_time = forms.TypedChoiceField(
        label="Horario",
        coerce=lambda value: value,
        empty_value=None,
    )
    appointment_date = forms.DateField(
        label="Fecha",
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"],
    )

    class Meta:
        model = Appointment
        fields = ["service", "appointment_date", "appointment_time", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Notas adicionales (opcional)"}),
        }

    def __init__(self, *args, **kwargs):
        time_choices = kwargs.pop("time_choices", None)
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = Service.objects.filter(is_active=True)
        for field in ("service", "appointment_date", "appointment_time"):
            self.fields[field].widget.attrs["class"] = "form-control"
        self.fields["service"].widget.attrs["class"] = "form-select"
        self.fields["appointment_time"].widget.attrs["class"] = "form-select"
        self.fields["appointment_date"].widget.attrs.setdefault("min", date.today().isoformat())
        # Ensure date inputs always use ISO format required by browsers
        self.fields["appointment_date"].widget.format = "%Y-%m-%d"
        self.fields["notes"].widget.attrs["class"] = "form-control"
        if time_choices is None:
            time_choices = [choice for choice, _ in TimeSlot.choices]
        formatted_choices = [(choice, choice) for choice in time_choices]
        self.fields["appointment_time"].choices = formatted_choices

    def clean_appointment_date(self):
        appointment_date = self.cleaned_data["appointment_date"]
        if appointment_date < datetime.today().date():
            raise forms.ValidationError("No podés reservar un turno en el pasado.")
        return appointment_date


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label="Nombre", max_length=30)
    last_name = forms.CharField(label="Apellido", max_length=30)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_classes = field.widget.attrs.get("class", "")
            merged_classes = f"{css_classes} form-control".strip()
            field.widget.attrs["class"] = merged_classes

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user
