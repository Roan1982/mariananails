# Mariana Nails Webapp

Aplicación web desarrollada con Django para gestionar la presencia digital del salón de manicuría Mariana Nails. Incluye página institucional, galería de trabajos, testimonios, formulario de contacto y sistema de turnos online con bloqueo automático de horarios ocupados.

## Requisitos

- Python 3.11+ (recomendado)
- [Pipenv](https://pipenv.pypa.io/) o `venv` para el entorno virtual
- Django 5.x (se instala a través de `pip install -r requirements.txt`)

## Puesta en marcha

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt  # crear este archivo según los paquetes instalados
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

La aplicación quedará disponible en `http://127.0.0.1:8000/`.

## Funcionalidades principales

- **Sitio institucional** con secciones de servicios, galería, historia y contacto.
- **Formulario de contacto** con almacenamiento en base de datos para seguimiento desde el panel de administración.
- **Valoraciones de clientas** vinculadas a usuarios registrados.
- **Sistema de turnos** con horarios predefinidos y bloqueo automático de los turnos reservados.
- **Autenticación completa** (registro, login, logout) basada en el sistema de usuarios de Django.
- **Botón flotante de WhatsApp** para contacto inmediato.
- **Panel de administración** para gestionar servicios, turnos, mensajes, galería y valoraciones.

## Próximos pasos recomendados

- Configurar envío de emails reales (`EMAIL_BACKEND`) para notificaciones.
- Agregar subida de imágenes reales en la galería (la app ya soporta archivos).
- Personalizar los horarios disponibles y duraciones de servicio según la agenda real.
- Desplegar en un proveedor (por ejemplo, Railway, Render, Fly.io) utilizando una base de datos gestionada.
