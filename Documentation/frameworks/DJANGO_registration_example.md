# Django registration template example

This example shows how to convert `Admin/src/pages-starter.html` and a registration page into Django templates.

1. Place HTML partials under `templates/partials/` and pages under `templates/pages/`.
2. Place static assets under `static/assets/` and update `STATICFILES_DIRS` if needed.

Example `templates/pages/registration.html`:

```html
{% extends 'base.html' %}
{% load static %}

{% block head %}
    <!-- Use the minified asset filename present in the repo -->
    <link rel="stylesheet" href="{% static 'assets/css/app.min.css' %}">
{% endblock %}

{% block content %}
    {# The page-title partial expects `title` and optional `subtitle` variables #}
    {% include 'partials/page-title.html' with subtitle='Auth' title='Register' %}

    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-body">
                    <form id="register-form" method="post" action="">
                        {% csrf_token %}
                        <div class="mb-3">
                            <label for="name" class="form-label">Full name</label>
                            <input type="text" class="form-control" id="name" name="name" placeholder="Enter your full name">
                        </div>
                        <div class="mb-3">
                            <label for="email" class="form-label">Email</label>
                            <input type="email" class="form-control" id="email" name="email" placeholder="Enter your email">
                        </div>
                        <div class="mb-3">
                            <label for="password" class="form-label">Password</label>
                            <input type="password" class="form-control" id="password" name="password" placeholder="Enter a password">
                        </div>
                        <button type="submit" class="btn btn-primary">Register</button>
                    </form>
                </div>
            </div>
        </div>
    </div>

{% endblock %}
```

This keeps asset references compatible with Django's static handling.
