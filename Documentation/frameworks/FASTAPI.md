# Hyper Template Integration: FastAPI Guide

This concise guide explains how to integrate the Hyper Bootstrap template into a FastAPI project, leveraging FastAPI’s performance and Starlette features.

## Goals

- Use Hyper’s HTML and assets in a FastAPI app
- Configure template folder and static files mount
- Convert Gulp `@@include()` syntax to Jinja2 includes

## Recommended Layout

```text
yourapp/
├─ app.py
├─ templates/
│  ├─ index.html
│  └─ partials/
│     ├─ head-css.html
│     ├─ title-meta.html
│     ├─ menu.html
│     └─ ...
└─ static/
   └─ assets/
      ├─ css/
      ├─ js/
      ├─ images/
      └─ vendor/...
```

## Dependencies

```bash
pip install fastapi uvicorn jinja2
```

## FastAPI App Setup

```python
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "Dashboard"})
```

## Converting Hyper Templates

### Includes and Variables

- Before: `@@include("./partials/title-meta.html", {"title": "Dashboard"})`
- After: `{% include 'partials/title-meta.html' %}`
- Variables: use `{{ title }}`

### Static Assets

- In HTML:

  ```html
  <link href="/static/assets/css/app.min.css" rel="stylesheet">
  ```

- Or using `request.url_for`:

  ```html
  <link href="{{ request.url_for('static', path='assets/css/app.min.css') }}" rel="stylesheet">
  ```

## Example `index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  {% include "partials/title-meta.html" %}
  <link href="/static/assets/vendor/daterangepicker/daterangepicker.css" rel="stylesheet">
  {% include "partials/head-css.html" %}
</head>
<body>
  {% include "partials/menu.html" %}

  <!-- Page content -->

  {% include "partials/footer.html" %}
  {% include "partials/footer-scripts.html" %}

  <script src="/static/assets/vendor/moment/moment.min.js"></script>
  <script src="/static/assets/js/pages/demo.dashboard.js"></script>
</body>
</html>
```

## Notes

- Ensure `app.mount` path matches your static folder.
- Pass `request` in template context for URL generation.
- You can customize Jinja2 environment for additional filters.
