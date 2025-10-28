# Hyper Admin Templates — Implementation Guide

Hyper Admin Templates deliver a catalog of production-ready dashboards, forms, widgets, charts, and UI patterns. This guide turns the repository into a reference manual so that developers (_who purchased a license for Hyper Admin Templates_) and LLMs can quickly assemble new pages (“three KPI cards on the left, a chart on the right, a data table below”) with minimal guesswork.

> **Need a visual preview?** Open any file under `base_templates/` in a browser to see the rendered output that matches the Django templates found in `templates/`.

## Table of Contents

- [Repository Overview](#repository-overview)
- [Quick Start](#quick-start)
- [Django Integration Guide](#django-integration-guide)
- [Template Architecture](#template-architecture)
- [Layout & Themes](#layout--themes)
- [Widgets](#widgets)
- [Component Catalog](#component-catalog)
- [Layout Recipes](#layout-recipes)
- [Adapting the Templates](#adapting-the-templates)
- [Troubleshooting & Tips](#troubleshooting--tips)
- [Credits & Plugins](#credits--plugins)
- [Reference Links](#reference-links)

---

## Repository Overview

```text
Hyper_v5.5.0/
├─ templates/             # Django-ready templates (extends, includes, blocks)
│  ├─ base.html           # Base wrapper used by every page
│  ├─ pages-*.html        # Authentication, pricing, FAQ, etc.
│  ├─ dashboard-*.html    # Analytics, CRM, Wallet, Projects
│  ├─ apps-*.html         # Email, Chat, Kanban, File Manager
│  ├─ charts-*.html       # ApexCharts, Chart.js, Sparkline demos
│  ├─ form-*.html         # Elements, validation, wizards, editors
│  ├─ tables-*.html       # Basic tables, DataTables integration
│  ├─ ui-*.html           # Cards, modals, accordions, typography, etc.
│  └─ partials/           # Header, menu, footer, head-css, scripts, etc.
├─ base_templates/        # Fully rendered HTML versions (open in browser)
├─ static/                # CSS, JS, images, vendor assets
└─ README.md              # You are here
```

- **templates/** is the authoritative source for Django usage. Each file extends `base.html` (or can easily be converted to do so) and relies on `{% include 'partials/...' %}`.
- **base_templates/** mirrors the same pages but as plain HTML files—ideal for confirming layout intent.
- **static/** hosts compiled CSS/JS, icon packs, charts libraries, and images referenced via `{% static '...' %}`.

---

## Quick Start

1. **Copy assets into your project.**
   - Place the `templates/` directory somewhere referenced by `TEMPLATES['DIRS']`.
   - Place the `static/` directory where Django can serve it (e.g., add it to `STATICFILES_DIRS`).
2. **Install dependencies.** Hyper is pure frontend. Only Django is required for templating; install extra chart/table libraries only if you remove the shipped vendor bundles.
3. **Verify rendering.** Start the Django dev server and open `/` mapped to one of the sample views provided below.

Example commands (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate
pip install django==5.1.2
django-admin startproject hyper_demo
Copy-Item -Recurse ..\Hyper_v5.5.0\templates .\hyper_demo\templates
Copy-Item -Recurse ..\Hyper_v5.5.0\static .\hyper_demo\static_hyper
cd hyper_demo
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) after wiring views as described next.

---

## Django Integration Guide

### settings.py (complete, copy/paste ready)

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
   "django.contrib.admin",
   "django.contrib.auth",
   "django.contrib.contenttypes",
   "django.contrib.sessions",
   "django.contrib.messages",
   "django.contrib.staticfiles",  # required for {% static %}
]

MIDDLEWARE = [
   "django.middleware.security.SecurityMiddleware",
   "django.contrib.sessions.middleware.SessionMiddleware",
   "django.middleware.common.CommonMiddleware",
   "django.middleware.csrf.CsrfViewMiddleware",
   "django.contrib.auth.middleware.AuthenticationMiddleware",
   "django.contrib.messages.middleware.MessageMiddleware",
   "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "hyper_demo.urls"

TEMPLATES = [
   {
      "BACKEND": "django.template.backends.django.DjangoTemplates",
      "DIRS": [BASE_DIR / "templates"],  # points to Hyper_v5.5.0/templates
      "APP_DIRS": True,
      "OPTIONS": {
         "context_processors": [
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
         ],
      },
   }
]

WSGI_APPLICATION = "hyper_demo.wsgi.application"

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static_hyper"]  # folder copied from Hyper/static
STATIC_ROOT = BASE_DIR / "staticfiles"          # where collectstatic copies files

# Optional: whitenoise for production
# MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
```

### urls.py

```python
from django.contrib import admin
from django.urls import path
from .views import DashboardView, EcommerceOrdersView, ComponentsView

urlpatterns = [
   path("admin/", admin.site.urls),
   path("", DashboardView.as_view(), name="dashboard"),
   path("orders/", EcommerceOrdersView.as_view(), name="orders"),
   path("components/", ComponentsView.as_view(), name="components"),
]
```

### views.py (class-based views returning template context)

```python
from django.views.generic import TemplateView


class DashboardView(TemplateView):
   template_name = "dashboard-analytics.html"

   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context.update(
         page_title="Analytics",
         kpi_cards=[
            {"title": "Active Users", "value": 121, "change": "+5.2%", "trend": "up"},
            {"title": "Views/min", "value": 560, "change": "-1.0%", "trend": "down"},
            {"title": "Campaign CTR", "value": "2.1%", "change": "+0.4%", "trend": "up"},
         ],
      )
      return context


class EcommerceOrdersView(TemplateView):
   template_name = "apps-ecommerce-orders.html"

   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context["page_title"] = "Orders"
      return context


class ComponentsView(TemplateView):
   template_name = "ui-cards.html"

   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context["page_title"] = "Components"
      return context
```

> **Tip:** Every template already includes `{% load static %}` where needed, but you can add global context (e.g., `page_title`) in `base.html` to avoid repeating logic.

### Running the demo

```powershell
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

Navigate to `/`, `/orders/`, `/components/` to view different pages using the Hyper templates.

---

## Template Architecture

### Base template (`templates/base.html`)

```django
{% extends 'base.html' %}  {# child usage #}

{% block title_meta %}
   {% include 'partials/title-meta.html' with title=page_title %}
{% endblock %}

{% block head_css %}
   {% include 'partials/head-css.html' %}
{% endblock %}

{% block page_title %}
   {% include 'partials/page-title.html' with subtitle=breadcrumb title=page_title %}
{% endblock %}

{% block content %}
   <!-- page body -->
{% endblock %}
```

Block summary:

- `title_meta`: override to supply the page `<title>` text and metadata.
- `head_css`: inject extra styles or plugin CSS before the closing `<head>`.
- `page_title`: renders the top breadcrumb/header section.
- `content`: main page body.
- `footer_scripts`: append page-specific JavaScript bundles (charts, tables, etc.).

### Key partials (all under `templates/partials/`)

- `html.html` – `<!DOCTYPE html>` shell.
- `menu.html` – wraps topbar, sidebar, and responsive navigation.
- `title-meta.html` – sets `<title>` and meta tags.
- `head-css.html` – theme CSS and icon libraries (`css/app.min.css`, `css/vendor.min.css`).
- `page-title.html` – breadcrumb and heading region.
- `footer.html` – footer layout.
- `right-sidebar.html` – theme customizer sidebar.
- `footer-scripts.html` – base JavaScript (`js/vendor.min.js`, `js/app.js`).
- `syntax-highlight.html` – optional highlight.js assets for code demos.

> **Adapting partials:** Copy to your project and tweak navigation items, logos, or footer text. Because templates use `{% include %}` you only change it once.

---

## Layout & Themes

Hyper provides extensive customization options for layouts and themes through HTML data attributes. All theming is controlled declaratively—no JavaScript configuration needed for basic theme changes.

### Theme Customization via Data Attributes

Hyper's layout engine reads data attributes from the `<html>` tag to apply different visual themes, layout modes, and sidebar configurations. These can be set dynamically in Django templates or views.

#### Available Data Attributes

| Attribute | Type | Options | Description |
|-----------|------|---------|-------------|
| `data-theme` | String | `"light"` \| `"dark"` | Overall color scheme (light or dark mode) |
| `data-layout` | String | `"vertical"` \| `"topnav"` | Main navigation position (sidebar or top) |
| `data-layout-mode` | String | `"fluid"` \| `"boxed"` \| `"detached"` | Container width and menu attachment |
| `data-topbar-color` | String | `"light"` \| `"dark"` \| `"brand"` | Topbar color scheme |
| `data-menu-color` | String | `"light"` \| `"dark"` \| `"brand"` | Sidebar/menu color scheme |
| `data-sidenav-size` | String | `"default"` \| `"compact"` \| `"condensed"` \| `"sm-hover"` \| `"full"` \| `"fullscreen"` | Sidebar width/size |
| `data-layout-position` | String | `"fixed"` \| `"scrollable"` | Whether layout scrolls or stays fixed |
| `data-sidenav-user` | Boolean | `"true"` \| `"false"` | Show/hide user info in sidebar |

### Django Integration: Dynamic Theming

You can control themes dynamically from your Django views or create a user preference system.

#### Method 1: Per-View Theme Control

```python
# views.py
from django.views.generic import TemplateView

class CustomThemeView(TemplateView):
    template_name = "custom-page.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Custom Dashboard',
            'theme_mode': 'dark',  # or 'light'
            'layout_mode': 'detached',  # or 'fluid', 'boxed'
            'menu_color': 'brand',  # or 'light', 'dark'
            'sidenav_size': 'condensed',  # or 'default', 'compact'
        })
        return context
```

Then in your template partial `templates/partials/html.html`:

```django
<!DOCTYPE html>
<html lang="en"
      {% if theme_mode %}data-theme="{{ theme_mode }}"{% endif %}
      {% if layout_mode %}data-layout-mode="{{ layout_mode }}"{% endif %}
      {% if menu_color %}data-menu-color="{{ menu_color }}"{% endif %}
      {% if sidenav_size %}data-sidenav-size="{{ sidenav_size }}"{% endif %}>
```

#### Method 2: User Preference Model

```python
# models.py
from django.db import models
from django.contrib.auth.models import User

class UserThemePreference(models.Model):
    THEME_CHOICES = [('light', 'Light'), ('dark', 'Dark')]
    LAYOUT_CHOICES = [('fluid', 'Fluid'), ('boxed', 'Boxed'), ('detached', 'Detached')]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    layout_mode = models.CharField(max_length=10, choices=LAYOUT_CHOICES, default='fluid')
    menu_color = models.CharField(max_length=10, default='dark')
    
    def __str__(self):
        return f"{self.user.username}'s theme preferences"

# context_processors.py
def theme_preferences(request):
    """Add user's theme preferences to all template contexts."""
    if request.user.is_authenticated:
        prefs, _ = UserThemePreference.objects.get_or_create(user=request.user)
        return {
            'theme_mode': prefs.theme,
            'layout_mode': prefs.layout_mode,
            'menu_color': prefs.menu_color,
        }
    return {'theme_mode': 'light', 'layout_mode': 'fluid', 'menu_color': 'dark'}
```

Add the context processor to `settings.py`:

```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ... other processors
                'yourapp.context_processors.theme_preferences',
            ],
        },
    }
]
```

### Pre-built Layout Examples

Hyper includes ready-made layout templates demonstrating different configurations. These are production-ready and can be used as base templates:

| Template File | Layout Type | Data Attributes | Use Case |
|--------------|-------------|-----------------|----------|
| `layouts-horizontal.html` | Top navigation | `data-layout="topnav"` | Apps with minimal navigation depth |
| `layouts-detached.html` | Detached sidebar | `data-layout-mode="detached"` | Modern, card-based layouts |
| `layouts-full.html` | Full-width | `data-layout-mode="fluid"` | Dashboards with wide charts/tables |
| `layouts-compact.html` | Compact sidebar | `data-sidenav-size="compact"` | Maximizing content area |
| `layouts-hover.html` | Hover-expand sidebar | `data-sidenav-size="sm-hover"` | Space-efficient navigation |
| `layouts-fullscreen.html` | Fullscreen | `data-sidenav-size="fullscreen"` | Immersive content experiences |

#### Example: Switching to Horizontal Layout

To use the horizontal (top navigation) layout:

1. **Set the data attribute** in your HTML tag:

   ```django
   <html lang="en" data-layout="topnav">
   ```

2. **Update your menu partial** to use horizontal navigation:

   In `templates/partials/menu.html`, replace the left sidebar include:

   ```django
   {# Remove or comment out: #}
   {# {% include 'partials/left-sidebar.html' %} #}
   
   {# Add horizontal navigation instead: #}
   {% include 'partials/horizontal-nav.html' %}
   ```

3. **See the example** in `templates/layouts-horizontal.html` for a complete working implementation.

#### Example: Detached Layout

For a modern, detached sidebar layout:

```django
{# templates/custom-detached-base.html #}
<!DOCTYPE html>
{% load static %}

<html lang="en" data-layout-mode="detached">
<head>
    {% include 'partials/title-meta.html' with title='My App' %}
    {% include 'partials/head-css.html' %}
</head>
<body>
    <div class="wrapper">
        {% include 'partials/topbar.html' %}
        {% include 'partials/left-sidebar.html' %}
        
        <div class="content-page">
            <div class="content">
                <div class="container-fluid">
                    {% block content %}{% endblock %}
                </div>
            </div>
            {% include 'partials/footer.html' %}
        </div>
    </div>
    {% include 'partials/footer-scripts.html' %}
</body>
</html>
```

### RTL (Right-to-Left) Support

Hyper includes built-in RTL support for Arabic, Hebrew, and other RTL languages.

To enable RTL:

1. **Add the `dir` attribute** to your HTML tag:

   ```django
   <html lang="ar" dir="rtl">
   ```

2. **Load the RTL stylesheet** in `templates/partials/head-css.html`:

   ```django
   {# Replace the standard CSS with RTL version #}
   <link href="{% static 'css/app-rtl.min.css' %}" rel="stylesheet" type="text/css" id="app-style">
   ```

   Or conditionally load based on user preference:

   ```django
   {% if is_rtl %}
       <link href="{% static 'css/app-rtl.min.css' %}" rel="stylesheet" type="text/css" id="app-style">
   {% else %}
       <link href="{% static 'css/app.min.css' %}" rel="stylesheet" type="text/css" id="app-style">
   {% endif %}
   ```

### Common Theme Configurations

Here are some popular theme combinations ready to copy:

#### Dark Mode with Compact Sidebar

```django
<html lang="en" 
      data-theme="dark" 
      data-menu-color="dark" 
      data-sidenav-size="compact">
```

#### Light Mode with Detached Layout

```django
<html lang="en" 
      data-theme="light" 
      data-layout-mode="detached" 
      data-menu-color="light">
```

#### Brand-Colored Top Navigation

```django
<html lang="en" 
      data-layout="topnav" 
      data-topbar-color="brand">
```

#### Minimal Hover Sidebar (Space-Saving)

```django
<html lang="en" 
      data-theme="light" 
      data-sidenav-size="sm-hover" 
      data-menu-color="dark">
```

### Testing Layouts Locally

To preview different layouts before integrating:

1. Open any layout example from `base_templates/layouts-*.html` in your browser
2. Inspect the `<html>` tag to see which data attributes are set
3. Copy the configuration to your Django template's `html.html` partial

### JavaScript Theme Switcher (Optional)

For runtime theme switching without page reload, Hyper includes `app.js` which provides:

```javascript
// Example: Let users toggle dark mode
document.getElementById('theme-toggle').addEventListener('click', function() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', newTheme);
    
    // Save preference to backend via AJAX
    fetch('/api/user/theme/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({theme: newTheme})
    });
});
```

The Hyper `app.js` automatically handles layout recalculations when attributes change.

---

## Widgets

Hyper's widget library spans KPI scorecards, timeline feeds, chat panes, todo lists, and chart-driven summaries. The canonical source is `templates/widgets.html`, which mirrors the official widgets documentation (`pages-demo-widget.html`) and is ready to drop into Django projects.

### Key Locations

- `templates/widgets.html` – Django template containing every widget variant.
- `base_templates/widgets.html` – Pre-rendered HTML preview for quick visual checks.
- `static/js/pages/demo.widgets.js` – Initializes ApexCharts sparklines and sample data.
- `static/js/ui/component.chat.js` – Provides chat widget behaviors and validation hooks.
- `static/js/ui/component.todo.js` – Powers the todo list interactions and relies on `vendor/moment`.

### Rendering KPI Widgets from Context

```python
from django.views.generic import TemplateView


class WidgetsView(TemplateView):
   template_name = "widgets.html"

   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context["kpi_widgets"] = [
         {
            "label": "Revenue",
            "value": "$6,254",
            "delta": "7.00%",
            "icon": "mdi-currency-btc",
            "trend_class": "badge bg-info",
            "trend_icon": "mdi-arrow-down-bold",
            "note": "Since last month",
         },
         {
            "label": "Growth",
            "value": "+ 30.56%",
            "delta": "4.87%",
            "icon": "mdi-pulse",
            "trend_class": "text-success",
            "trend_icon": "mdi-arrow-up-bold",
            "note": "Since last month",
         },
      ]
      return context
```

```django
<div class="row">
   {% for widget in kpi_widgets %}
      <div class="col-xxl-3 col-sm-6">
         <div class="card widget-flat">
            <div class="card-body">
               <div class="float-end">
                  <i class="mdi {{ widget.icon }} widget-icon"></i>
               </div>
               <h5 class="text-muted fw-normal mt-0">{{ widget.label }}</h5>
               <h3 class="mt-3 mb-3">{{ widget.value }}</h3>
               <p class="mb-0 text-muted">
                  <span class="{{ widget.trend_class }} me-2">
                     <i class="mdi {{ widget.trend_icon }}"></i> {{ widget.delta }}
                  </span>
                  <span class="text-nowrap">{{ widget.note }}</span>
               </p>
            </div>
         </div>
      </div>
   {% endfor %}
</div>
```

### Chart and Sparkline Widgets

Include the required vendor scripts and the demo initializer via the `footer_scripts` block. Replace the sample data inside `demo.widgets.js` with live results when wiring to your API.

```django
{% block footer_scripts %}
   {{ block.super }}
   <script src="{% static 'vendor/apexcharts/apexcharts.min.js' %}"></script>
   <script src="{% static 'vendor/moment/moment.min.js' %}"></script>
   <script src="{% static 'js/ui/component.chat.js' %}"></script>
   <script src="{% static 'js/ui/component.todo.js' %}"></script>
   <script src="{% static 'js/pages/demo.widgets.js' %}"></script>
{% endblock %}
```

`data-colors` attributes on the chart containers (for example, `<div id="sales-spark" class="apex-charts" data-colors="#3688fc">`) let you override palettes without editing JavaScript.

### Interactive Widgets

- Chat conversation pane with typing form; validation and scroll behavior come from `component.chat.js`.
- Todo list with add/archive actions; `component.todo.js` exposes hooks to persist tasks server-side.
- Timeline and transaction feeds use `data-simplebar` to supply smooth scroll areas.
- Profile, inbox, and contact cards pair avatars with CTA buttons for quick actions.

### Styling and Extensibility

If you maintain the original SCSS pipeline, edit `src/assets/scss/custom/components/_widgets.scss` before recompiling. In this repo you can append overrides by adding a custom stylesheet in `partials/head-css.html` (for example, `{% static 'css/custom-widgets.css' %}`) so classes such as `widget-flat`, `tilebox-one`, and `text-bg-*` match your brand. Extract recurring groups into partials (e.g., `partials/widgets/kpi-row.html`) when you want reusable widget sets.

### Quick Start Checklist

- Copy the desired widget markup from `templates/widgets.html` into your page or dedicated partial.
- Add the `footer_scripts` block above so charts, chat, and todo widgets load their JavaScript.
- Feed live data via Django context or template tags instead of placeholder numbers.
- Override colors or spacing with a custom stylesheet loaded after `css/app.min.css`.

---

## Component Catalog

Every component showcased in the demo has a source template you can copy, customize, or fragment into smaller includes. The list below highlights the most frequently reused pieces.

### KPI & Statistic Cards

- Source templates: `index.html`, `dashboard-analytics.html`, `widgets.html`.
- Classes used: `card widget-flat`, `card tilebox-one`.
- Example snippet:

```html
<div class="col-sm-6 col-xl-3">
   <div class="card widget-flat">
      <div class="card-body">
         <div class="float-end"><i class="mdi mdi-account-multiple widget-icon"></i></div>
         <h5 class="text-muted fw-normal mt-0">Customers</h5>
         <h3 class="mt-3 mb-3">36,254</h3>
         <p class="mb-0 text-muted"><span class="text-success me-2"><i class="mdi mdi-arrow-up-bold"></i> 5.27%</span> Since last month</p>
      </div>
   </div>
</div>
```

### Charts

- ApexCharts demos: `charts-apex-*.html` (area, bar, radial, heatmap, timeline).
- Chart.js demos: `charts-chartjs-*.html`.
- Sparkline cards: `widgets.html` (`#sales-spark` etc.).
- Include required vendor JS in the `footer_scripts` block, e.g.:

```django
{% block footer_scripts %}
   {{ block.super }}
   <script src="{% static 'vendor/apexcharts/apexcharts.min.js' %}"></script>
   <script src="{% static 'js/pages/demo.dashboard.js' %}"></script>
{% endblock %}
```

### Data Tables

- Basic table markup: `tables-basic.html`.
- Feature-rich DataTables: `tables-datatable.html`.
- Required CSS/JS: `vendor/datatables/*` (already referenced in template head/footer).
- Example markup for a responsive table:

```html
<table id="basic-datatable" class="table table-striped dt-responsive nowrap w-100">
   <thead>
      <tr><th>Name</th><th>Position</th><th>Office</th><th>Age</th><th>Start date</th><th>Salary</th></tr>
   </thead>
   <tbody> ... </tbody>
</table>
```

### Forms & Validation

- Standard controls: `form-elements.html`.
- Advanced plugins (date pickers, select2, etc.): `form-advanced.html`.
- Form wizards/steps: `form-wizard.html`.
- Validation examples: `form-validation.html` (includes `js/pages/demo.form-validation.js`).

### Layout Helpers

- Grid examples: `ui-grid.html` for bootstrap columns & offsets.
- Offcanvas navigation: `ui-offcanvas.html`.
- Modals/alerts/toasts: `ui-modals.html`, `ui-alerts.html`, `ui-notifications.html`.
- Ready hero/landing page: `landing.html`.

For fast experimentation, open the equivalent file under `base_templates/` to see the final look, then copy JSX/HTML back into your Django page.

---

## Layout Recipes

Below are walk-throughs for common page structures. Each recipe links back to exemplar templates so you can reuse CSS classes and JS bundles.

### 1. Dashboard with KPI cards, chart, and data table

**Goal:** Top row shows three KPI cards on the left and a chart on the right; below them a full-width data table.

1. **View logic (optional)** – supply KPI values and table data.

   ```python
   from django.views.generic import TemplateView

   class CustomDashboardView(TemplateView):
      template_name = "pages-starter.html"

      def get_context_data(self, **kwargs):
         context = super().get_context_data(**kwargs)
         context.update(
            page_title="Performance",
            breadcrumb="Dashboards",
            kpis=[
               {"icon": "mdi-account-multiple", "title": "Customers", "value": "12,480", "delta": "+4.2%"},
               {"icon": "mdi-cart-plus", "title": "Orders", "value": "1,842", "delta": "+1.8%"},
               {"icon": "mdi-currency-usd", "title": "Revenue", "value": "$84k", "delta": "-0.7%"},
            ],
            recent_orders=[
               {"id": "#1001", "customer": "Sarah Connor", "total": "$199", "status": "Paid"},
               {"id": "#1002", "customer": "John Carter", "total": "$459", "status": "Pending"},
            ],
         )
         return context
   ```

2. **Template** – extend `base.html` and compose sections.

   ```django
   {% extends 'base.html' %}

   {% block title_meta %}
      {% include 'partials/title-meta.html' with title=page_title %}
   {% endblock %}

   {% block page_title %}
      {% include 'partials/page-title.html' with subtitle=breadcrumb title=page_title %}
   {% endblock %}

   {% block head_css %}
      {{ block.super }}
      <link rel="stylesheet" href="{% static 'vendor/datatables/buttons.bootstrap5.min.css' %}">
   {% endblock %}

   {% block content %}
      <div class="row">
         <div class="col-xl-5 col-lg-6">
            <div class="row">
               {% for card in kpis %}
                  <div class="col-sm-6">
                     <div class="card widget-flat">
                        <div class="card-body">
                           <div class="float-end"><i class="mdi {{ card.icon }} widget-icon"></i></div>
                           <h5 class="text-muted fw-normal mt-0">{{ card.title }}</h5>
                           <h3 class="mt-3 mb-3">{{ card.value }}</h3>
                           <p class="mb-0 text-muted">{{ card.delta }} since last month</p>
                        </div>
                     </div>
                  </div>
               {% endfor %}
            </div>
         </div>

         <div class="col-xl-7 col-lg-6">
            <div class="card card-h-100">
               <div class="card-body">
                  <div id="revenue-chart" class="apex-charts" data-colors="#3688fc,#42d29d"></div>
               </div>
            </div>
         </div>
      </div>

      <div class="row mt-4">
         <div class="col-12">
            <div class="card">
               <div class="card-body">
                  <h4 class="header-title">Recent Orders</h4>
                  <table id="orders-table" class="table table-centered table-hover align-middle dt-responsive nowrap w-100">
                     <thead><tr><th>ID</th><th>Customer</th><th>Total</th><th>Status</th></tr></thead>
                     <tbody>
                        {% for order in recent_orders %}
                           <tr>
                              <td>{{ order.id }}</td>
                              <td>{{ order.customer }}</td>
                              <td>{{ order.total }}</td>
                              <td>{{ order.status }}</td>
                           </tr>
                        {% endfor %}
                     </tbody>
                  </table>
               </div>
            </div>
         </div>
      </div>
   {% endblock %}

   {% block footer_scripts %}
      {{ block.super }}
      <script src="{% static 'vendor/apexcharts/apexcharts.min.js' %}"></script>
      <script src="{% static 'vendor/datatables/jquery.dataTables.min.js' %}"></script>
      <script src="{% static 'vendor/datatables/dataTables.bootstrap5.min.js' %}"></script>
      <script>
         document.addEventListener("DOMContentLoaded", function () {
            const options = {
               chart: { type: "line", height: 300 },
               series: [
                  { name: "Revenue", data: [31, 40, 28, 51, 42, 109, 100] },
                  { name: "Orders", data: [11, 32, 45, 32, 34, 52, 41] },
               ],
               xaxis: { categories: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] },
            };
            new ApexCharts(document.querySelector("#revenue-chart"), options).render();
            window.jQuery && jQuery("#orders-table").DataTable();
         });
      </script>
   {% endblock %}
   ```

3. **Result:** Layout mimics `index.html` from the theme but driven by your context data.

### 2. Multi-step Form Wizard

1. Reference `form-wizard.html` for HTML structure (uses `data-bs-target` and `data-wizard` attributes).
2. Copy step markup into your page and include `js/pages/demo.form-wizard.js` inside `footer_scripts`.
3. To validate each step, reuse validation classes from `form-validation.html`.

### 3. CRUD Table with Filters

1. Start from `apps-ecommerce-orders.html` for layout (filters + table + summary cards).
2. Replace static data with template loops (`{% for order in orders %}`).
3. Use Django forms or query parameters to handle filters; render selected state inside `<select>` elements.
4. Hook into DataTables events to load async data if needed (see `tables-datatable.html`).

---

## Adapting the Templates

- **Change brand assets:** Update logos and favicons in `static/images/` and adjust references in `partials/menu.html` and `partials/title-meta.html`.
- **Navigation structure:** Modify `partials/menu.html` once; all pages inherit the new layout.
- **Global theming:** Override CSS tokens by appending a new stylesheet inside `head_css` or editing `css/app.min.css` (if you control the build pipeline).
- **JavaScript behavior:** Each demo page loads plugin initialization scripts from `js/pages/*.js`. Copy, rename, or write new modules that target your DOM IDs.
- **Internationalization:** Replace literal text with `{% trans %}` tags or inject dictionaries via context processors.

When reusing components, favor copying from `templates/` (keeps Django tags intact) and check `base_templates/` for visual confirmation.

---

## Troubleshooting & Tips

- **Missing assets?** Confirm `STATICFILES_DIRS` points at the Hyper `static/` folder and that `collectstatic` runs without errors.
- **Blank page sections?** Ensure your template overrides the correct block names (`title_meta`, `page_title`, `content`).
- **JS errors in console?** Verify the required vendor scripts are included. Many chart/table demos expect initialization code located under `static/js/pages/`.
- **Large bundle size?** Remove unused chart libraries from `footer_scripts` and delete unused CSS references.
- **Need REST data?** Render components with static HTML first, then progressively enhance using fetch/AJAX by targeting the same DOM IDs used in the demos.

---

## Credits & Plugins

The Hyper Admin Templates are built with a carefully curated collection of third-party libraries and plugins. When using these templates in Django, all required assets are already included in the `static/` directory and referenced via `{% static %}` tags in the templates.

### Core Framework & UI

| Plugin | URL | Usage in Templates |
|--------|-----|-------------------|
| **Bootstrap** | <https://getbootstrap.com/> | Base responsive framework (v5.3.3) |
| **jQuery** | <https://jquery.com/> | DOM manipulation and plugin support |
| **Simplebar** | <https://github.com/Grsmto/simplebar> | Custom scrollbars |

### Icons

| Plugin | URL | Usage in Templates |
|--------|-----|-------------------|
| **Material Design Icons** | <https://materialdesignicons.com/> | Primary icon set (`mdi-*` classes) |
| **Remixicon** | <https://remixicon.com/> | Alternative icon set |
| **Unicons** | <https://iconscout.com/unicons> | Additional icons |
| **Lucide Icons** | Included in distribution | Modern icon alternatives |

### Charts & Data Visualization

| Plugin | URL | Usage in Templates |
|--------|-----|-------------------|
| **ApexCharts** | <https://apexcharts.com/> | Primary charting library (area, bar, line, pie, radar, etc.) |
| **Chart.js** | <https://www.chartjs.org/> | Alternative charting (area, bar, line) |
| **Sparklines** | <https://omnipotent.net/jquery.sparkline/> | Inline mini charts |
| **Brite Charts** | <https://github.com/eventbrite/britecharts> | D3-based charts |
| **ECharts** | Included in distribution | Enterprise charting library |

### Tables

| Plugin | URL | Usage in Templates |
|--------|-----|-------------------|
| **DataTables** | <https://datatables.net/> | Advanced table features (sorting, filtering, pagination) |

### Forms & Input

| Plugin | URL | Usage in Templates |
|--------|-----|-------------------|
| **Select2** | <https://select2.org/> | Enhanced select dropdowns |
| **Flatpickr** | <https://flatpickr.js.org/> | Modern date/time picker |
| **Daterangepicker** | <http://www.daterangepicker.com/> | Date range selection |
| **Bootstrap Datepicker** | <https://bootstrap-datepicker.readthedocs.io/> | Alternative date picker |
| **Bootstrap Timepicker** | <https://jdewit.github.io/bootstrap-timepicker/> | Time selection |
| **Input Mask** | <https://github.com/igorescobar/jQuery-Mask-Plugin> | Input formatting/masking |
| **Bootstrap Touchspin** | <https://github.com/istvan-ujjmeszaros/bootstrap-touchspin> | Numeric spinner |
| **Bootstrap Maxlength** | <https://mimo84.github.io/bootstrap-maxlength/> | Character counter |
| **Typeahead** | <https://twitter.github.io/typeahead.js/> | Autocomplete |
| **Dropzone.js** | <https://www.dropzonejs.com/> | File upload with preview |

### Editors

| Plugin | URL | Usage in Templates |
|--------|-----|-------------------|
| **Summernote** | <https://summernote.org/> | WYSIWYG editor |
| **SimpleMDE** | <https://simplemde.com/> | Markdown editor |

### UI Components & Interactions

| Plugin | URL | Usage in Templates |
|--------|-----|-------------------|
| **Dragula** | <https://github.com/bevacqua/dragula> | Drag-and-drop functionality |
| **Ion Range Slider** | <http://ionden.com/a/plugins/ion.rangeSlider/> | Range slider component |
| **RateIt** | <https://github.com/gjunge/rateit.js> | Star rating widget |
| **Toast** | <https://kamranahmed.info/toast> | Notification toasts |

### Application Plugins

| Plugin | URL | Usage in Templates |
|--------|-----|-------------------|
| **FullCalendar** | <https://fullcalendar.io/> | Calendar/event management (`apps-calendar.html`) |
| **Frappe Gantt** | <https://frappe.io/gantt> | Gantt chart (`apps-projects-gantt.html`) |
| **Form Wizard** | <http://vinceg.github.io/twitter-bootstrap-wizard/> | Multi-step forms (`form-wizard.html`) |

### Maps

| Plugin | URL | Usage in Templates |
|--------|-----|-------------------|
| **GMaps** | <https://hpneo.github.io/gmaps/examples.html> | Google Maps integration |
| **JVectorMap** | <http://jvectormap.com/> | Vector map visualization |

### Graphics & Illustrations

| Resource | URL | Usage in Templates |
|----------|-----|-------------------|
| **unDraw** | <https://undraw.co/illustrations> | SVG illustrations used throughout |

### Django Integration Notes

All these plugins are:

- **Pre-bundled** in `static/vendor/` with minified versions
- **Pre-configured** in templates with correct `{% static %}` paths
- **Loaded conditionally** – only pages that need specific plugins include their scripts

When deploying with Django:

1. Copy the entire `static/` directory to your project
2. Add it to `STATICFILES_DIRS` in settings
3. Run `python manage.py collectstatic` for production
4. Templates will automatically reference assets via `{% static 'vendor/...' %}`

You do **not** need to install these libraries separately via npm or pip – they're ready to use as static files. Each plugin's official documentation (linked above) provides details on customization and advanced features.

---

## Reference Links

- Hyper previews (`base_templates/`): open locally with `python -m http.server`.
- Django template language: <https://docs.djangoproject.com/en/stable/topics/templates/>
- Django static files: <https://docs.djangoproject.com/en/stable/howto/static-files/>
- Bootstrap 5 documentation: <https://getbootstrap.com/docs/5.3/getting-started/introduction/>
- ApexCharts documentation: <https://apexcharts.com/docs/>
- DataTables documentation: <https://datatables.net/>

With these references and the recipes above, you can compose new dashboards, admin tools, or marketing pages quickly while staying consistent with the Hyper visual language.
