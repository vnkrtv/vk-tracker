FROM python:latest
MAINTAINER LeadNess
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt /
  && django-admin.py startproject VKInfoSite /
  && python VKInfoSite/manage.py startapp main /
  && python VKInfoSite/manage.py startapp vksearch /
  && python VKInfoSite/manage.py startapp dashboard
COPY VKInfoSite /app/VKInfoSite
ENTRYPOINT ["python", "/app/VKInfoSite/manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
