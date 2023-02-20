FROM python:3

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

RUN apt-get update \
 && apt-get -y upgrade
 && pip install --upgrade pip

RUN mkdir -p /var/www
COPY ./requirements.txt /var/www
RUN pip install --no-cache-dir -r /var/www/requirements.txt

RUN python --version

COPY ./*.py /var/www

WORKDIR /var/www

CMD ["gunicorn", "main:app", "--config", "/var/www/gunicorn.py" ]
