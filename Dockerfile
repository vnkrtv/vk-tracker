FROM python:latest
MAINTAINER LeadNess

COPY requirements.txt /app/requirements.txt
COPY VKInfoSite /app/VKInfoSite

RUN pip3 install --no-cache-dir -r requirements.txt /
  && python3 /app/manage.py makemigrations /
  && python3 /app/manage.py migrate /
  && echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '', 'admin')" | python3 /app/VKInfoSite/manage.py shell

EXPOSE 8000

ENTRYPOINT ["python3", "/app/VKInfoSite/manage.py", "runserver", "0.0.0.0:80", "--noreload"]
