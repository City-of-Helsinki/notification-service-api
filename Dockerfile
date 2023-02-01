# ==============================
FROM helsinkitest/python:3.7-slim as appbase
# ==============================
RUN mkdir /entrypoint

COPY --chown=appuser:appuser requirements.txt /app/requirements.txt
COPY --chown=appuser:appuser requirements-prod.txt /app/requirements-prod.txt

RUN apt-install.sh \
        git \
        netcat \
        libpq-dev \
        build-essential \
    && pip install -U pip \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir  -r /app/requirements-prod.txt \
    && apt-cleanup.sh build-essential

COPY --chown=appuser:appuser docker-entrypoint.sh /entrypoint/docker-entrypoint.sh
ENTRYPOINT ["/entrypoint/docker-entrypoint.sh"]

# ==============================
FROM appbase as development
# ==============================

COPY --chown=appuser:appuser requirements-dev.txt /app/requirements-dev.txt
RUN apt-install.sh \
        build-essential \
    && pip install --no-cache-dir -r /app/requirements-dev.txt \
    && apt-cleanup.sh build-essential

ENV DEV_SERVER=1

COPY --chown=appuser:appuser . /app/

USER appuser
EXPOSE 8081/tcp

# ==============================
FROM appbase as production
# ==============================

COPY --chown=appuser:appuser . /app/

RUN SECRET_KEY="only-used-for-collectstatic" python manage.py collectstatic

# OpenShift write accesses, pycache is created to "/app/quriiri"
USER root
RUN chgrp -R 0 /app/quriiri && chmod g+w -R /app/quriiri

USER appuser
EXPOSE 8000/tcp
