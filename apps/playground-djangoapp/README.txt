# eave_django_playground

Eave demo app to test Django inter-op.

Creates a `polls` app following the django tutorial
https://docs.djangoproject.com/en/5.0/intro/tutorial01/

The only way to create new questions/choices is to use the django admin panel at `{url}/admin/`.

TODO: setup client tracing in base_site.html and base.html 
TODO: instrument django web + db in asgi.py/wsgi.py ???
