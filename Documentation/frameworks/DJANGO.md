# Hyper Template Integration: Django Guide

This guide explains how to integrate the Hyper Bootstrap template into a Django project while following Django’s conventions for templates and static files.

## Goals

- Use Hyper’s HTML and assets in Django
- Replace build-time includes with Django template includes
- Serve assets via Django staticfiles

> **Note:** This guide uses Django’s built-in templating engine (Django Template Language, DTL). DTL tags `{% ... %}` and `{{ ... }}` are used, with `{% load static %}` for assets.

## Recommended Layout

Use project-level folders with `templates/` and `static/` as siblings (preferred for clarity and simplicity):

```
yourproject/
├─ templates/
│  ├─ index.html
│  └─ partials/
│     ├─ head-css.html
│     ├─ title-meta.html
│     ├─ menu.html
│     ├─ footer.html
│     ├─ right-sidebar.html
│     └─ ...
├─ static/
│  ├─ assets/
│  │  ├─ css/
│  │  ├─ js/
│  │  ├─ images/
│  │  └─ vendor/...
└─ yourproject/
   └─ settings.py
```

Alternative: if you prefer bundling into a dedicated app, mirror the same structure under the app:

```text
yourproject/
├─ <app_name>/           # replace with your Django app's name
│  ├─ templates/
│  │  ├─ index.html
│  │  └─ partials/
│  │     ├─ head-css.html
│  │     ├─ title-meta.html
│  │     ├─ menu.html
│  │     ├─ footer.html
│  │     ├─ right-sidebar.html
│  │     └─ ...
│  └─ static/
│     └─ assets/
│        ├─ css/
│        ├─ js/
│        ├─ images/
│        └─ vendor/...
└─ yourproject/
  └─ settings.py
```

## Django Settings

Add or confirm these in `settings.py`:

```python
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    # 'hyper_ui',  # if using dedicated app
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # if using project-level templates
        'APP_DIRS': True,  # enables app/templates lookup
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # project-level static next to templates
STATIC_ROOT = BASE_DIR / 'staticfiles'    # for collectstatic in production
```

## Converting Hyper Templates

Replace Gulp includes and variables with Django syntax and static tags.

### Includes

- Before: `@@include("./partials/title-meta.html", {"title": "Dashboard"})`
- After: `{% include "partials/title-meta.html" %}`
  - Pass variables from the view (see below).

### Variables

- Before: `@@title`
- After: `{{ title }}`

### Static assets

- Before: `<link href="assets/css/app.min.css" rel="stylesheet">`
- After:

  ```django
  {% load static %}
  <link href="{% static 'assets/css/app.min.css' %}" rel="stylesheet">
  ```

## Example Partials

`templates/partials/title-meta.html`

```html
<meta charset="utf-8" />
<title>{{ title|default:'Dashboard' }} | Hyper - Responsive Bootstrap 5 Admin Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta content="A fully featured admin theme which can be used to build CRM, CMS, etc." name="description" />
<meta content="Coderthemes" name="author" />
<link rel="shortcut icon" href="{% static 'assets/images/favicon.ico' %}">
```

## Example Page Template

`templates/index.html`

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  {% include "partials/title-meta.html" %}
  <link href="{% static 'assets/vendor/daterangepicker/daterangepicker.css' %}" rel="stylesheet">
  <link href="{% static 'assets/vendor/jsvectormap/jsvectormap.min.css' %}" rel="stylesheet">
  {% include "partials/head-css.html" %}
</head>
<body>
  <div class="wrapper">
  {% include "partials/menu.html" %}

    <!-- page content here -->

  {% include "partials/footer.html" %}
  </div>

  {% include "partials/right-sidebar.html" %}
  {% include "partials/footer-scripts.html" %}

  <script src="{% static 'assets/vendor/moment/moment.min.js' %}"></script>
  <script src="{% static 'hyper/assets/vendor/daterangepicker/daterangepicker.js' %}"></script>
  <script src="{% static 'hyper/assets/vendor/apexcharts/apexcharts.min.js' %}"></script>
  <script src="{% static 'hyper/assets/vendor/jsvectormap/jsvectormap.min.js' %}"></script>
  <script src="{% static 'hyper/assets/vendor/jsvectormap/world-merc.js' %}"></script>
  <script src="{% static 'hyper/assets/vendor/jsvectormap/world.js' %}"></script>
  <script src="{% static 'assets/js/pages/demo.dashboard.js' %}"></script>
</body>
</html>
```

## Views and URLs

```python
# views.py
from django.shortcuts import render

def dashboard(request):
  return render(request, 'index.html', {'title': 'Dashboard'})
```

```python
# urls.py
from django.urls import path
from .views import dashboard

urlpatterns = [
  path('', dashboard, name='dashboard'),
]
```

## Production Notes

- Run `python manage.py collectstatic` before deployment.
- Ensure all vendor assets live under `static/hyper/assets/...` and are referenced through `{% static %}`.
- Consider refactoring to a base layout later with `{% extends 'hyper/base.html' %}` and `{% block %}`s.

## Troubleshooting

- 404 static files → check `{% load static %}` and paths, verify STATICFILES_DIRS/STATIC_ROOT.
- Includes not found → ensure paths are template-relative (e.g., `hyper/partials/...`).
- Variables not rendering → ensure they’re passed via view context or use defaults (`{{ var|default:'...' }}`).
