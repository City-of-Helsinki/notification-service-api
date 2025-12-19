# ==============================
FROM registry.access.redhat.com/ubi9/python-312 AS appbase
# ==============================

# Branch or tag used to pull python-uwsgi-common.
ARG UWSGI_COMMON_REF=main

USER root
WORKDIR /app

COPY --chown=default:root requirements.txt /app/requirements.txt

RUN dnf update -y && dnf install -y nc \
    && pip install -U pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && uwsgi --build-plugin https://github.com/City-of-Helsinki/uwsgi-sentry \
    && mkdir -p /usr/local/lib/uwsgi/plugins \
    && mv sentry_plugin.so /usr/local/lib/uwsgi/plugins/ \
    # Entrypoint:
    # - checks db connectivity
    # - does migration if requested
    # - does initial admin account setup if requested
    # - starts the server (runs manage.py or wsgi)
    && mkdir /entrypoint \
    && dnf clean all

# Build and copy specific python-uwsgi-common files.
ADD https://github.com/City-of-Helsinki/python-uwsgi-common/archive/${UWSGI_COMMON_REF}.tar.gz /usr/src/
RUN mkdir -p /usr/src/python-uwsgi-common && \
    tar --strip-components=1 -xzf /usr/src/${UWSGI_COMMON_REF}.tar.gz -C /usr/src/python-uwsgi-common && \
    mkdir /etc/uwsgi && \
    cp /usr/src/python-uwsgi-common/uwsgi-base.ini /etc/uwsgi/ && \
    uwsgi --build-plugin /usr/src/python-uwsgi-common && \
    rm -rf /usr/src/${UWSGI_COMMON_REF}.tar.gz && \
    rm -rf /usr/src/python-uwsgi-common

COPY --chown=default:root docker-entrypoint.sh /entrypoint/docker-entrypoint.sh
CMD ["/usr/bin/bash", "/entrypoint/docker-entrypoint.sh"]

# ==============================
FROM appbase AS development
# ==============================

COPY --chown=default:root requirements-dev.txt /app/requirements-dev.txt

ENV DEV_SERVER=1

COPY --chown=default:root . /app/

RUN pip install --no-cache-dir -r /app/requirements-dev.txt && \
    git config --system --add safe.directory /app

# Set permissions for cache directories
RUN mkdir -p /app/.pytest_cache /app/.ruff_cache && \
    chown -R default:root /app/.pytest_cache /app/.ruff_cache && \
    chmod -R a+rwx /app/.pytest_cache /app/.ruff_cache

USER default
EXPOSE 8081/tcp

# ==============================
FROM appbase AS production
# ==============================

COPY --chown=default:root . /app/

# fatal: detected dubious ownership in repository at '/app'
RUN git config --system --add safe.directory /app && \
    SECRET_KEY="only-used-for-collectstatic" python manage.py collectstatic && \
    # OpenShift write accesses, __pycache__ is created to "/app/quriiri"
    chgrp -R 0 /app/quriiri && chmod g+w -R /app/quriiri

USER default
EXPOSE 8000/tcp
