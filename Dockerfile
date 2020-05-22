FROM amancevice/pandas:latest
MAINTAINER LeadNess

RUN apt-get update \
 && apt-get install -y libc-dev \
 && apt-get install -y build-essential python3 \
 && apt-get install -y python3-setuptools \
 && apt-get install -y python3-pip \
 && python3 -m pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
COPY VKInfoSite /app/VKInfoSite
COPY deploy/container_settings /app/VKInfoSite/VKInfoSite/settings.py

RUN pip3 install --no-cache-dir -r /app/requirements.txt \
 && file="$(echo "$(cat /usr/local/lib/python3.7/site-packages/pymongo/mongo_client.py)")" \
 && echo "${file}" | sed 's/HOST = "localhost"/HOST = "mongo"/' > /usr/local/lib/python3.7/site-packages/pymongo/mongo_client.py

COPY deploy/entrypoint /entrypoint
ENTRYPOINT ["/entrypoint"]
