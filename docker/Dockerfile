FROM python:latest
WORKDIR /app
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt && django-admin.py startproject VKInfoSite && python VKInfoSite/manage.py startapp main
COPY VKInfoSite /app/VKInfoSite
ENTRYPOINT ["python", "/app/VKInfoSite/manage.py", "runserver", "0.0.0.0:8000", "--noreload"]
