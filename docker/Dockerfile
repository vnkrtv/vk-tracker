FROM python:latest
MAINTAINER LeadNess
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt /
  && django-admin.py startproject VKInfoSite /
  && python /app/VKInfoSite/manage.py startapp main /
  && python /app/VKInfoSite/manage.py startapp vksearch /
  && python /app/VKInfoSite/manage.py startapp dashboard /
  && echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '', 'admin')" | python /app/VKInfoSite/manage.py shell
COPY VKInfoSite /app/VKInfoSite
EXPOSE 80
ENTRYPOINT ["python", "/app/VKInfoSite/manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
