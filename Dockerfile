FROM python:3

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

RUN apt-get update \
 && pip install --upgrade pip

RUN mkdir -p /var/www
COPY ./requirements.txt /var/www
RUN pip install --no-cache-dir -r /var/www/requirements.txt

RUN python --version

COPY ./flask_app.py /var/www
COPY ./gunicorn.py /var/www

WORKDIR /var/www

CMD ["gunicorn", "flask_app:app", "--config", "/var/www/gunicorn.py" ]
