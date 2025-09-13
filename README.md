# Hyper Admin Templates v5.5.0

Welcome to the Hyper Admin Templates repository (v5.5.0), a comprehensive collection of standalone HTML admin pages, ready-to-use partials, and framework integration guides. These templates are built on top of Hyper’s modern UI components and can be consumed directly in any web server or integrated into popular Python frameworks.

---

## Table of Contents

* [Hyper Admin Templates v5.5.0](#hyper-admin-templates-v550)
  * [Table of Contents](#table-of-contents)
  * [Overview](#overview)
  * [Getting Started](#getting-started)
  * [Project Structure](#project-structure)
  * [Using with an LLM](#using-with-an-llm)
  * [Framework Integrations](#framework-integrations)
    * [Django](#django)
    * [Flask](#flask)
    * [Flask](#flask-1)
    * [FastAPI](#fastapi)
    * [FastAPI](#fastapi-1)
  * [Previewing Locally](#previewing-locally)
  * [Contributing](#contributing)
  * [License](#license)

---

## Overview

Hyper Admin Templates provides a suite of fully designed admin pages and interface components, including:

- Dashboards (Analytics, CRM, Projects, Wallet)
- Apps (Chat, Calendar, E-Commerce, CRM, File Manager, Kanban, etc.)
- Data visualizations (ApexCharts, Chart.js, BriteCharts, Sparkline)
- Forms, Wizards, Editors, Validation, File Uploads
- Extended components (ScrollSpy, Treeview, Ratings, Range Slider)
- Icon libraries (Lucide, Material Design, RemixIcons, Unicons)
- Layout demos (Horizontal, Detached, Fullscreen, Hover, Compact)

Each page in `Admin/src/` is self-contained and composes common fragments via Gulp’s `@@include()` syntax.


## Getting Started

1. Clone this repository:

   ```bash
   git clone https://github.com/your-org/hyper-admin-templates.git
   cd hyper-admin-templates
   ```

2. Install or serve static files (no build step required):

2. Install or serve static files (no build step required):

   ```bash
   cd Admin/src
   python -m http.server 8000
   ```

3. Open `http://localhost:8000/index.html` in your browser.

3. Open `http://localhost:8000/index.html` in your browser.


## Project Structure

```text
.
├── Admin/
│   └── src/                # All standalone HTML pages
│       ├── index.html      # Landing page
│       ├── dashboard-*.html
│       ├── apps-*.html
│       ├── charts-*.html
│       └── partials/       # Header, footer, sidebar, components
│
├── Documentation/
│   └── frameworks/         # Integration guides for Django, Flask, FastAPI
│       ├── DJANGO.md
│       ├── FLASK.md
│       └── FASTAPI.md
│
├── Starter-Kit/            # React/Vue scaffold (optional)
│   └── src/
│
└── LICENSE
```


## Using with an LLM

Leverage an LLM (e.g., OpenAI GPT, Azure OpenAI, Anthropic Claude) to automate common tasks:

- **Template Conversion**: Prompt the model to replace `@@include('partials/foo.html')` with `{% include 'partials/foo.html' %}` (Django) or `{{ include('partials/foo.html') }}` (Jinja2).
- **Bulk Refactoring**: Generate scripts or mapping functions to update asset paths (CSS, JS, images) when migrating to a different static folder or CDN.
- **Content Preview**: Ask the LLM to extract metadata (page titles, descriptions) from each template for automated documentation or site maps.


## Framework Integrations

### Django

1. Copy `Admin/src/` into your Django `templates/` directory.
2. Install static files under `STATIC_ROOT` and set in `settings.py`:

   ```py
   STATIC_URL = '/static/'
   STATICFILES_DIRS = [BASE_DIR / 'Hyper/Admin/src/assets']
   ```

3. Convert Gulp includes:
3. Convert Gulp includes:

   ```html
   <!-- before -->
   @@include('partials/header.html')
   <!-- after -->
   {% include 'partials/header.html' %}
   ```

### Flask
4. Load templates in views:
   ```py
   def dashboard(request):
       return render(request, 'dashboard-analytics.html')
   ```

### Flask

1. `pip install Flask`
2. In `app.py`:

   ```py
   from flask import Flask, render_template

   app = Flask(__name__,
       template_folder='Admin/src',
       static_folder='Admin/src/assets'
   )

   @app.route('/')
   def index():
       return render_template('index.html')

   if __name__ == '__main__':
       app.run(debug=True)
   ```

### FastAPI
3. Use Jinja2 `{% include %}` syntax in templates as above.

### FastAPI

1. `pip install fastapi uvicorn`
2. In `main.py`:

   ```py
   from fastapi import FastAPI, Request
   from fastapi.staticfiles import StaticFiles
   from fastapi.templating import Jinja2Templates

   app = FastAPI()
   app.mount('/static', StaticFiles(directory='Admin/src/assets'), name='static')
   templates = Jinja2Templates(directory='Admin/src')

   @app.get('/')
   async def index(request: Request):
       return templates.TemplateResponse('index.html', {'request': request})
   ```


## Previewing Locally

Use any static server pointing at `Admin/src`:

- Python: `python -m http.server 8000`
- Node.js: `npx serve Admin/src`
- VS Code Live Server extension


## Contributing

1. Fork the repo.
2. Create a branch: `git checkout -b feature/my-new-page`
3. Add or update HTML in `Admin/src` or docs in `Documentation/frameworks`.
4. Submit a pull request and describe your changes.


## License

This project is released under the [MIT License](./LICENSE).
