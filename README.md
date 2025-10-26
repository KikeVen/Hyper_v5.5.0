# Hyper Admin Templates — Implementation Guide

Hyper Admin Templates deliver a catalog of production-ready dashboards, forms, widgets, charts, and UI patterns. This guide turns the repository into a reference manual so that developers and LLMs can quickly assemble new pages (“three KPI cards on the left, a chart on the right, a data table below”) with minimal guesswork.

> **Need a visual preview?** Open any file under `base_templates/` in a browser to see the rendered output that matches the Django templates found in `templates/`.

## Table of Contents

- [Repository Overview](#repository-overview)
- [Quick Start](#quick-start)
- [Django Integration Guide](#django-integration-guide)
- [Template Architecture](#template-architecture)
- [Component Catalog](#component-catalog)
- [Layout Recipes](#layout-recipes)
- [Adapting the Templates](#adapting-the-templates)
- [Troubleshooting & Tips](#troubleshooting--tips)
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

## Reference Links

- Hyper previews (`base_templates/`): open locally with `python -m http.server`.
- Django template language: <https://docs.djangoproject.com/en/stable/topics/templates/>
- Django static files: <https://docs.djangoproject.com/en/stable/howto/static-files/>
- Bootstrap 5 documentation: <https://getbootstrap.com/docs/5.3/getting-started/introduction/>
- ApexCharts documentation: <https://apexcharts.com/docs/>
- DataTables documentation: <https://datatables.net/>

With these references and the recipes above, you can compose new dashboards, admin tools, or marketing pages quickly while staying consistent with the Hyper visual language.
