# Hyper Template Integration: Flask Guide

This concise guide explains how to integrate the Hyper Bootstrap template into a Flask project, leveraging Flask’s flexible folder structure and built-in helpers.

## Goals

- Use Hyper’s HTML and assets in a Flask app
- Configure `template_folder` and `static_folder`
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

## Flask App Setup

```python
from flask import Flask, render_template

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

@app.route("/")
def dashboard():
    return render_template("index.html", title="Dashboard")

if __name__ == "__main__":
    app.run(debug=True)
```

## Converting Hyper Templates

### Includes and Variables

- Before: `@@include("./partials/title-meta.html", {"title": "Dashboard"})`
- After: `{% include 'partials/title-meta.html' %}`
- Variables: use `{{ title }}`

### Static Assets

- Before:

  ```html
  <link href="assets/css/app.min.css" rel="stylesheet">
  ```
- After:

  ```html
  <link href="{{ url_for('static', filename='assets/css/app.min.css') }}" rel="stylesheet">
  ```

## Example `index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  {% include "partials/title-meta.html" %}
  <link href="{{ url_for('static', filename='assets/css/app.min.css') }}" rel="stylesheet">
  {% include "partials/head-css.html" %}
</head>
<body>
  {% include "partials/menu.html" %}

  <!-- Page content -->

  {% include "partials/footer.html" %}
  {% include "partials/footer-scripts.html" %}

  <script src="{{ url_for('static', filename='assets/js/app.min.js') }}"></script>
</body>
</html>
```

## Notes

- Adjust asset paths if your `static/` folder is nested differently.
- Use `url_for('static', filename=...)` to generate correct URLs.

