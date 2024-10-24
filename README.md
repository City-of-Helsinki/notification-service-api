# Notification service API

[![status](https://travis-ci.com/City-of-Helsinki/notification-service-api.svg)](https://github.com/City-of-Helsinki/notification-service-api)
[![codecov](https://codecov.io/gh/City-of-Helsinki/notification-service-api/branch/develop/graph/badge.svg)](https://codecov.io/gh/City-of-Helsinki/notification-service-api)

The Notification service API is a Django REST Framework API for sending notifications via SMS, email, and push notifications. The API is designed to be used by other services to send notifications to users.

## Deployment environments

### TODO: FIXME!

- [Development](https://api.hel.fi/notification-service/v1/)
- [Staging](https://api.hel.fi/notification-service/v1/)
- [Production](https://api.hel.fi/notification-service/v1/)

## Prerequisites

These are the prerequisites to run the project. If you apply these instructions to another containerization platform, you may need to adjust the instructions accordingly.

### Docker

Version 27.3.1 has been confirmed to work at the time of this writing. You can check your version by running `docker --version`.

These instructions have been confirmed to apply running Docker either at localhost or on a remote machine, including virtual machines. If you are running Docker on a remote machine, you may need to forward ports to your local machine.

### Docker Compose

If you don't have a `docker compose` subcommand, you may need to install the latest version of Docker. If you have a `docker-compose` command available but no `docker compose`, and `docker-compose` is version 2.x, you need to edit `~/.docker/config.json` in order to add its directory under the `cliPluginsExtraDirs` key (which is an array of directories).

- On macOS, if you have Docker installed with homebrew, that directory is `/opt/homebrew/lib/docker/cli-plugins`.
- On Debian Linux, it's in the `/usr/libexec/docker/cli-plugins` directory.
- Although the following example includes both, pick either, or what's appropriate for your distribution:

```json
{
  "cliPluginsExtraDirs": [
    "/opt/homebrew/lib/docker/cli-plugins",
    "/usr/libexec/docker/cli-plugins"
  ]
}
```

## Dependencies

These are the basic internal dependencies of the project. If you are running the project without Docker, you may need to install these dependencies manually.

### Python

Python 3.11 is the minimum version required. You can check your version by running `python --version`.

If you encounter deprecation warnings on newer versions, you may need to downgrade to Python 3.11, but ideally fix the deprecation warnings and upgrade the container's python base version.

### PostgreSQL

Postgresql 13 is the minimum version required. You can check your version by running `psql --version`.

If you are running the project without Docker, you may need to install and configure PostgreSQL manually. The default configuration file is `docker-compose.env.yaml`, which you may need to adjust for your local setup.

### Keycloak

Keycloak is used for authentication and authorization. You can check your version by running `docker exec notification-service-keycloak /opt/jboss/keycloak/bin/standalone.sh --version`.

### Quriiri

Quriiri is a Finnish SMS gateway service. You can check your version by running `curl https://api.quriiri.fi/v1/ --header "Authorization: Bearer <your_api_key>"`. You need to have an API key to use the service. The API key is set in the `docker-compose.env.yaml` file.

### Other

Other dependencies are listed in the `requirements.txt` and `requirements-dev.txt` files. You can install them by running `pip install -r requirements.txt` and `pip install -r requirements-dev.txt`.

## Getting started

These are instructions of running the project with Docker. If you are running the project without Docker, you may need to adjust the instructions accordingly. There are (likely outdated) instructions in [a separate documentiation for running without Docker](./docs/development-without-docker.md), which you can refer to.

### Setup the environment configuration file.

Copy `docker-compose.env.yaml.example` to `docker-compose.env.yaml`. It does work out of the box by default, but modify it according to your specific needs, if any.

If you are not running postgresql as a part of the docker compose set, ensure the database variables `DATABASE_URL` and `DATABASE_HOST` are set correctly.

By default, they point to the default internal hosts of the container network of an unconfigured example.

### Configure the keycloak hostname into /etc/hosts

#### TODO: ideally get rid of this step!

Add the following line to your hosts file (`/etc/hosts` on mac and linux):
`hosts
    127.0.0.1       notification-service-keycloak
    `

If the docker host is on a remote or virtual machine at another interface, make ssh tunnels to the virtual machine, forwarding the required ports (8081 and 8180) to your localhost, such as:
`shell
    ssh -L8081:localhost:8081 -L8180:localhost:8180 container_host
    `

### Run the compose file

Execute `docker compose up` in your shell.

Use `docker compose up --force-recreate --build` if you have made changes to environmental variables or have made other untracked changes.

### Inspect the services.

#### The Keycloak admin interface should be available at:

- http://notification-service-keycloak:8180/admin
- The keycloak interface defaults to username "admin" and password "keycloak".
- The defaults are initially set in the [`docker-compose.keycloak.env.yaml`](./keycloak/docker-compose.keycloak.env.yaml) file.

#### The API should be available at:

- http://localhost:8081/v1/

The django admin page is available in http://localhost:8081/admin.
An admin user can be created with `python manage.py add_admin_user -u admin -p adminpass -e admin@example.com`. To run the same command into a Docker container, use `docker exec -it django python manage.py add_admin_user -u admin -p adminpass -e admin@example.com`.

## About Keycloak

The Keycloak development realm for this project is preconfigured with the name "local-dev". The basic configuration is derived from the file [`realm.json`](./keycloak/realm.json), which is imported during the build process.

The Realm parameters can be modified through environmental variables in [`docker-compose.keycloak.env.yaml`](./keycloak/docker-compose.keycloak.env.yaml) and [`docker-compose.env.yaml`](./docker-compose.env.yaml).

It's important to ensure matching parameters between the configuration files and the running Keycloak instance. Otherwise, the default authentication flow won't work correctly.

### Configuration of additional parameters

Additional parameters can be configured via the Keycloak admin interface.

Navigate to the appropriate realm ("local-dev") and review the parameters in the clients, users, and realm settings sections.

NOTE: Keep in mind that any changes made to parameters will be lost if you recreate and rebuild the containers without exporting the realm(s) first.

### Configuration

At the moment the API only integrate with Quriiri SMS gateway.

To use the Quriiri sender, you need to have Quriiri API Key and API URL, then add them to the [docker-compose.env.yaml](./docker-compose.env.yaml). If running locally, to your local `.env`:

```
QURIIRI_API_KEY = <your_quriiri_api_key>
QURIIRI_API_URL = <quriiri_api_url>
```

### API Authentication

The API using default [DRF TokenAuthentication](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication). You need to generate an API token for each client by using CLI
command.

NOTE: You have to create API client user first, by login to Django Admin interface using Admin account:
`shell
    python manage.py drf_create_token <username>
    `

- After that, include the auth token to the every request to Notification Service. For example:
  ```shell
  curl --location --request POST 'https://api.hel.fi/notification-service/v1/message/send' \
  --header 'Authorization: Token <Auth Token>' \
  --header 'Content-Type: application/json' \
  --data-raw '{
    "sender": "Hel.fi",
    "to": [
      {
        "destination": "+012345678",
        "format": "MOBILE"
      }
    ],
    "text": "SMS message"
  }'
  ```

## API Documentation

### TODO: FIXME!

- [Swagger Hub](https://app.swaggerhub.com/apis-docs/t0mim/NotificationService/1.0.1)

## Keeping Python requirements up to date

1. Install `pip-tools`:

   - `pip install pip-tools`

2. Add new packages to `requirements.in` or `requirements-dev.in`

3. Update `.txt` file for the changed requirements file:

   - `pip-compile requirements.in`
   - `pip-compile requirements-dev.in`

4. If you want to update dependencies to their newest versions, run:

   - `pip-compile --upgrade requirements.in`

5. To install Python requirements run:

   - `pip-sync requirements.txt`

6. To install Python development requirements run:

   - `pip-sync requirements-dev.txt`

7. To install Python production requirements run:

   - `pip-sync requirements.txt requirements-prod.txt`

## Code formatting

This project uses [`ruff`](https://docs.astral.sh/ruff/formatter/) for Python code formatting. Basic `ruff` commands:

`ruff format` is the primary entrypoint to the formatter. It accepts a list of files or directories, and formats all discovered Python files:

```
ruff format                   # Format all files in the current directory.
ruff format path/to/code/     # Format all files in `path/to/code` (and any subdirectories).
ruff format path/to/file.py   # Format a single file.
```

> Similar to Black, running ruff format /path/to/file.py will format the given file or directory in-place, while ruff format --check /path/to/file.py will avoid writing any formatted files back, and instead exit with a non-zero status code upon detecting any unformatted files.

To run the Ruff Linter use `ruff check`.

> `ruff check` is the primary entrypoint to the Ruff linter. It accepts a list of files or directories, and lints all discovered Python files, optionally fixing any fixable errors:

```
ruff check                  # Lint all files in the current directory.
ruff check --fix            # Lint all files in the current directory, and fix any fixable errors.
ruff check --watch          # Lint all files in the current directory, and re-lint on change.
ruff check path/to/code/    # Lint all files in `path/to/code` (and any subdirectories).
```

1. Install `pre-commit` (there are many ways to do but let's use pip as an example):
   - `pip install pre-commit`
2. Set up git hooks from `.pre-commit-config.yaml`, run this command from project root:
   - `pre-commit install`

After that, formatting hooks will run against all changed files before committing
