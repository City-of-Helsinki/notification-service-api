# ==============================
FROM registry.access.redhat.com/ubi9/python-311 AS appbase
# ==============================

USER root
WORKDIR /app

COPY --chown=default:root requirements.txt /app/requirements.txt
COPY --chown=default:root requirements-prod.txt /app/requirements-prod.txt

RUN yum update -y && yum install -y nc && \
    pip install -U pip setuptools wheel && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    pip install --no-cache-dir  -r /app/requirements-prod.txt && \
    # Entrypoint:
    # - checks db connectivity
    # - does migration if requested
    # - does initial admin account setup if requested
    # - starts the server (runs manage.py or wcgi)
    mkdir /entrypoint

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
