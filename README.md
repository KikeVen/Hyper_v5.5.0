# Hyper Admin Templates — Django conversion quickstart

This repository contains static HTML templates and assets for the Hyper admin theme. The templates are largely ready for Django integration; this README provides quick instructions, a conversion checklist, and recommended settings for using these files in a Django project.

Quickstart (3 steps)

1) Copy or point Django to these folders:
   - Templates: add the templates/ directory to your Django TEMPLATES['DIRS'].
   - Static: add the static/ directory to STATICFILES_DIRS (or copy files into your project's static source).

2) Minimal settings.py snippets:
   - Ensure 'django.contrib.staticfiles' is in INSTALLED_APPS.
   - Set STATIC_URL = '/static/'
   - Set STATICFILES_DIRS to include the path to this repo's static/ folder.
   - Set STATIC_ROOT = BASE_DIR / 'staticfiles' for production collectstatic.

3) Test run (example commands):
   - python manage.py collectstatic --noinput
   - python manage.py runserver

Conversion checklist

- Replace legacy placeholders like @@title / @@subtitle with Django variables ({{ title }} / {{ subtitle }}).
- Ensure {% load static %} is present in the base template.
- Use {% static 'path/to/file' %} for asset links.
- Normalize include paths to reference partials/ (e.g., {% include 'partials/topbar.html' %}).
- Add {% csrf_token %} to forms where applicable.

Changes applied in this repository

- Replaced @@title/@@subtitle placeholders in templates/partials/title-meta.html and templates/partials/page-title.html.
- Normalized includes in templates/partials/menu.html to reference templates/partials/*.

Notes and next steps

- Consider renaming pages-starter.html to base.html or adding templates/base.html that includes it.
- Optionally run a regex pass to find other @@... placeholders; I can provide and run that if you want.

References

- Django templates: [https://docs.djangoproject.com/en/stable/topics/templates/](https://docs.djangoproject.com/en/stable/topics/templates/)
- Static files: [https://docs.djangoproject.com/en/stable/howto/static-files/](https://docs.djangoproject.com/en/stable/howto/static-files/)
