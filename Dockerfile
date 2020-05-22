FROM python:3.6.8-alpine
MAINTAINER LeadNess

COPY requirements.txt /app/requirements.txt
COPY VKInfoSite /app/VKInfoSite
COPY deploy/container_settings /app/VKInfoSite/VKInfoSite/settings.py

RUN pip3 install --no-cache-dir -r /app/requirements.txt \
  && python3 /app/manage.py makemigrations \
  && python3 /app/manage.py migrate \
  && echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '', 'admin')" | python3 /app/VKInfoSite/manage.py shell

EXPOSE 80

ENTRYPOINT ["python3", "/app/VKInfoSite/manage.py", "runserver", "0.0.0.0:80", "--noreload"]
