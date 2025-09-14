# Hyper Admin Templates v5.5.0

Welcome to the Hyper Admin Templates repository (v5.5.0), a comprehensive collection of standalone HTML admin pages, ready-to-use partials, and framework integration guides. These templates are built on top of Hyper’s modern UI components and can be consumed directly in any web server or integrated into popular Python frameworks.

---

## Table of Contents

* [Hyper Admin Templates v5.5.0](#hyper-admin-templates-v550)
  * [Table of Contents](#table-of-contents)
  * [Framework integrations and recommended mapping](#framework-integrations-and-recommended-mapping)
    * [Django (recommended mapping)](#django-recommended-mapping)
    * [Flask / Jinja2 (recommended mapping)](#flask--jinja2-recommended-mapping)
    * [FastAPI (Jinja2 via starlette/jinja2)](#fastapi-jinja2-via-starlettejinja2)
    * [Assistant guidance (important)](#assistant-guidance-important)
  * [Building pages from components (assistant workflow)](#building-pages-from-components-assistant-workflow)
  * [Partials quick reference](#partials-quick-reference)
  * [Previewing Locally](#previewing-locally)
    * [Important note about includes and previewing](#important-note-about-includes-and-previewing)
  * [License](#license)

## Framework integrations and recommended mapping

These templates are intended to be integrated into server frameworks (Django, Flask, FastAPI). When adapting them, prefer the framework's default folder names and conventions for templates and static files (for example `templates/` and `static/`) instead of requiring an `Admin/` folder at that exact path. The assistant should adapt file locations, include syntax, and static paths to the target framework when converting pages.

High-level guidance:

* Don't require the user to create an `Admin/` folder in their project. Instead, copy or move the contents of `Admin/src/` into the framework's `templates/` directory and copy `Admin/src/assets/` into the framework's `static/` directory (or configure the framework to serve from that assets path).
* Replace Gulp `@@include()` directives with the framework's include syntax and update asset references to use the framework's static helpers (`{% static %}` in Django, `url_for('static', ...)` in Flask/Jinja2, or mounted `/static` in FastAPI).
* Use `Admin/src/pages-starter.html` as the canonical base template when assembling a page to adapt to a framework — it already includes the main scaffolding (top nav, side nav, footer and scripts).

Below are concise, copy-paste examples showing the recommended mapping and include/static conversions.

### Django (recommended mapping)

Suggested actions:

* Place converted templates into `your_project/templates/` (for example `templates/partials/` and `templates/pages/`).
* Place static assets into `your_project/static/` (or set `STATICFILES_DIRS` to point at the `Admin/src/assets` folder).

Example `settings.py` snippet:

```py
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']  # or BASE_DIR / 'path' / 'to' / 'assets'
```

Example template conversions:

* Convert includes:

```html
<!-- before -->
@@include('./partials/menu.html')
<!-- after (Django) -->
{% include 'partials/menu.html' %}
```

* Convert asset links (add `{% load static %}` once in the top-level template):

```html
{% load static %}
<link rel="stylesheet" href="{% static 'assets/css/app.css' %}">
<script src="{% static 'assets/js/app.js' %}"></script>
```

This keeps templates compatible with Django's template loader and static file handling.

### Flask / Jinja2 (recommended mapping)

Suggested actions:

* Copy converted templates into `templates/` and assets into `static/` (project root).
* In templates use Jinja2 `include` and `url_for('static', ...)` helpers.

Example minimal `app.py` (Flask defaults):

```py
from flask import Flask, render_template

app = Flask(__name__)  # defaults: templates/ and static/

@app.route('/')
def index():
   return render_template('index.html')

if __name__ == '__main__':
   app.run(debug=True)
```

Example template conversions:

```html
<!-- include -->
{% include 'partials/menu.html' %}

<!-- asset link -->
<link rel="stylesheet" href="{{ url_for('static', filename='assets/css/app.css') }}">
```

If you prefer not to copy files, you can also set `Flask(__name__, template_folder='Admin/src', static_folder='Admin/src/assets')`, but using `templates/` and `static/` keeps projects idiomatic.

### FastAPI (Jinja2 via starlette/jinja2)

Suggested actions:

* Copy converted templates into `templates/` and assets into `static/` (project root), or mount `Admin/src/assets` at `/static`.

Example `main.py` using Jinja2Templates:

```py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

@app.get('/')
async def index(request: Request):
   return templates.TemplateResponse('index.html', {'request': request})
```

In templates, reference static assets using the `/static` path (or `url_for` helpers if available in your Jinja2 setup):

```html
<link rel="stylesheet" href="/static/assets/css/app.css">
```

### Assistant guidance (important)

When asked to adapt or "build" pages for a specific framework, the assistant should:

1. Use `Admin/src/pages-starter.html` as the base scaffolding when generating a final page.
2. Recursively replace `@@include('./partials/*.html')` with the equivalent framework include syntax (for Django/Jinja2 use `{% include %}`, etc.).
3. Update asset references to the framework's static path helpers (`{% static %}`, `url_for('static', ...)`, or `/static/...`) and advise the user where to place the `assets/` files in the target project.
4. Prefer the target framework's default folder names (`templates/` and `static/`) — do not force the creation of an `Admin/` folder unless the user asks for it.

Following these rules will make the converted pages integrate cleanly with typical Django, Flask, and FastAPI projects.

Assistant checklist (quick):

* Confirm whether the user wants a flattened (static) HTML file or framework templates; do not assume flattened output.
* If producing a flattened file, start from `Admin/src/pages-starter.html` and resolve all `@@include()` directives.
* If producing framework templates, convert `@@include()` to the framework's include syntax and update asset helpers (`{% static %}`, `url_for('static', ...)`, or `/static/...`).
* Do not commit `Admin/dist/` flattened outputs to the repo — treat them as demo-only and keep them local unless the user explicitly requests otherwise.
* When in doubt, ask one clarifying question (flattened vs template target) before generating files.

## Building pages from components (assistant workflow)

When a user asks the assistant to "create" or "build" a new page (for example: "Create a registration form, use `form-elements.html` as a guide" or "Create a page listing all user phone calls in a table showing date, phone number, duration"), the assistant should follow this workflow:

1. Start from the canonical base: `Admin/src/pages-starter.html` (this ensures the top nav, side nav, footer and scripts are present).
2. Identify which partials or example pages contain the components needed. Common sources:

  * Forms and inputs: `form-elements.html`, `form-validation.html`, `form-wizard.html`.
  * Tables and lists: any `apps-*.html` or `crm-*.html` pages; `apps-ecommerce-orders.html` and `tables-datatable.html` show table patterns.
  * Page structure and titles: `page-title.html` and `title-meta.html`.

3. Compose the requested page by inserting the required partials or markup into the main content area within `pages-starter.html`:

   * Replace or augment the content inside the `<div class="container-fluid">` area used in `pages-starter.html`.

   * Include page-specific partials (for example `@@include('./partials/page-title.html', {"subtitle":"Auth","title":"Register"})`) or write inline markup drawn from sample pages.

4. Resolve includes (if producing a flattened HTML) or convert `@@include()` to the framework's include syntax for the target environment.

5. Update asset references to use the framework static helper or ensure paths remain valid for static hosting.

Small contract to follow when generating a page (assistant should state this up-front):

* Inputs: user's request (page purpose and required fields/components), target framework (optional), any design constraints.
* Outputs: a complete HTML page (or set of templates/partials) that uses the project's components and follows the framework's include/static conventions.
* Error modes: if a requested component doesn't exist, propose the closest sample partial and ask the user to confirm or provide missing details.

Edge cases to check for every generated page:

* Missing component: if the exact component (for example a calendar widget) isn't available, suggest a fallback and include a note.
* Asset path collisions: ensure CSS/JS paths are not duplicated or conflicting with existing project assets.
* Form actions: generated forms should include placeholder `action` attributes or explicit guidance on wiring to backend endpoints.

Examples

* Registration form: "Create a registration form, use `form-elements.html` as a guide."
  * Assistant steps: copy relevant inputs and validation markup from `form-elements.html`, add a `page-title` include, place the form inside the `.container-fluid` area of `pages-starter.html`, convert includes and asset links for the target framework.

* Calls list page: "Create a page listing all the users phone calls in a table showing date, phone number, duration."
  * Assistant steps: find a table example (e.g., `apps-ecommerce-orders.html`), copy the table structure, adapt columns to `date`, `phone_number`, `duration`, include sorting/pagination notes if requested, and insert into the content area of `pages-starter.html`.

When the user asks "build index.html" or similar, the assistant should confirm the target (flattened HTML vs framework templates). If the user wants a flattened HTML, resolve all `@@include()` directives into a single HTML file using `pages-starter.html` as the base and make sure all referenced assets are reachable from the output location.

Canonical `base.html` (recommended)

When converting these pages into framework templates, it's helpful to create a single `base.html` that provides the shared scaffolding (head includes, top menu, footer and script includes) and exposes `head`, `content`, and `scripts` blocks. The following `base.html` is intentionally framework-agnostic (uses Jinja/Django style blocks/includes) and matches the approach used in `Documentation/frameworks/DJANGO_registration_example.md`:

```html
<!doctype html>
<html lang="en">
  <head>
    {% include 'partials/title-meta.html' %}
    {% include 'partials/head-css.html' %}
    {% block head %}{% endblock %}
  </head>
  <body>
    {% include 'partials/menu.html' %}

    <main class="container">
      {% block content %}{% endblock %}
    </main>

    {% include 'partials/footer.html' %}
    {% include 'partials/footer-scripts.html' %}

    {% block scripts %}{% endblock %}
  </body>
</html>
```

How to use `base.html` when generating pages

* For Django and Jinja2 (Flask / FastAPI with Jinja2): pages should extend the `base.html` and fill the `head`, `content`, and optionally `scripts` blocks. See `Documentation/frameworks/DJANGO_registration_example.md` for a concrete registration example that follows this pattern.
* When creating a flattened/static preview instead of framework templates, keep `pages-starter.html` as the canonical base (it already contains the full scaffolding) and resolve `@@include()` directives into the final HTML.

This keeps generated pages consistent across frameworks: flattened builds use `pages-starter.html`, and framework-adapted templates extend a shared `base.html` that pulls partials from `partials/`.

## Partials quick reference

All partials live under `Admin/src/partials/`. Common partials used across pages include:

* `html.html` (opening HTML tag + doctype)
* `title-meta.html` (page title and meta tags)
* `head-css.html` (CSS and vendor CSS includes)
* `menu.html` (top/side navigation; this is the wrapper that draws the top bar and side menu)
* `page-title.html` (page title/subtitle block)
* `footer.html` (page footer)
* `right-sidebar.html` (optional right sidebar)
* `footer-scripts.html` (vendor JS and page scripts)

When building a final, distributable page you should ensure the resulting HTML contains the menu and header partials so the top nav and side nav are present in the final output.

## Previewing Locally

### Important note about includes and previewing

Files inside `Admin/src/` use the `@@include()` directive to compose pages from partials. A basic static server (for example `python -m http.server`) will serve the files but will NOT expand these includes. This means pages like `index.html` may appear broken when opened directly from the server because the header/menu/footer fragments are not expanded.

Two ways to preview correctly:

1. Use a build step to resolve the includes into a single flattened HTML file (recommended for static previews).
2. Integrate templates into your framework (Django/Flask/FastAPI) and convert the `@@include()` directives into your engine's `{% include %}` or equivalent.

Example local preview (no conversion):

```bash
cd Admin/src
python -m http.server 8000
open http://localhost:8000/index.html
```

But to preview final pages with all partials included, use a build/conversion step. See the optional include resolver below for a tiny script you can use.

Optional: a tiny include resolver

If you want to generate a single built HTML file from a page that uses `@@include()` directives, a small script can be used to expand them. This is intentionally simple (no JS execution) and works for straightforward partials include patterns. The repo contains a demo helper at `tools/include_resolver.py` which offers these convenient flags:

* `--copy-assets` — copy `Admin/src/assets/` into the output folder so the flattened file is self-contained (recommended for local preview).
* `--validate` — run sanity checks (single html/head/body, missing includes, missing local assets) and exit non-zero on problems.

Try the demo resolver (PowerShell example):

```powershell
# Build a self-contained preview of the starter page
python .\tools\include_resolver.py --input Admin/src/pages-starter.html --output Admin/dist/index.html --copy-assets --validate

# Build a single page (registration example) for quick preview
python .\tools\include_resolver.py --input Admin/src/examples/registration-page.html --output Admin/dist/registration.html --copy-assets --validate
```

This demo script is provided for convenience only. When you build a final `index.html` for distribution or for asking Copilot to "build index.html", the base file to use is `Admin/src/pages-starter.html`. `pages-starter.html` already includes the main site scaffolding (top nav, side nav, footer and scripts). A Copilot-generated or scripted build should:

* Read `Admin/src/pages-starter.html` as the base template.
* Recursively resolve `@@include('./partials/*.html')` occurrences by inserting their file contents.
* Ensure references to assets remain correct (e.g., `/assets/css/...` or relative `assets/...`) and map them to your target static hosting path if needed.

This guarantees the built file contains all components (top nav, side nav, footer, right-sidebar, and the footer-scripts) and can be served directly as a single HTML page.

Important: "dist" outputs are demo-only

We intentionally include an optional `Admin/dist/` output path in some helper scripts for local demonstration, but assistants and automated tooling should NOT create or assume `dist` files as part of a framework integration. Reason:

* Different frameworks expect different template/static layouts and helper tags. A flattened HTML in `Admin/dist/` may work for static hosting but will not be appropriate for Django/Flask/FastAPI where templates belong in `templates/` and assets belong in `static/`.
* When converting for a framework, instead convert the `@@include()` directives to the framework's include syntax and map `Admin/src/assets/` into the project's static folder. Only generate flattened `dist` files on explicit user request for local preview or static hosting.

If you're an assistant: ask whether the user wants a flattened demo file (in which case use `pages-starter.html` and clearly label the output as demo-only) or framework-adapted templates (in which case produce templates under `templates/` and update asset references to use the framework's static helpers).

## License

This project is released under the [Hyper Admin Dashboard Template License](./LICENSE).
