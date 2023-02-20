FROM python:3

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on

RUN apt-get update \
 && apt-get -y upgrade \
 && curl -o /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
 && dpkg -i /tmp/google-chrome-stable_current_amd64.deb; exit 0
 
RUN rm -f /tmp/google-chrome-stable_current_amd64.deb \
 && apt-get install -y -f \
 && apt-get clean \
 && pip install --upgrade pip \
 && mkdir -p /var/www

COPY ./requirements.txt /var/www
RUN pip install --no-cache-dir -r /var/www/requirements.txt \
 && pip cache purge \
 && python --version \
 && cat /proc/version \
 && cat /etc/os-release

COPY ./*.py /var/www

WORKDIR /var/www

CMD ["gunicorn", "main:app", "--config", "/var/www/gunicorn.py" ]
