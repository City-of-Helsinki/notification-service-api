# Notification service API


[![status](https://travis-ci.com/City-of-Helsinki/notification-service-api.svg)](https://github.com/City-of-Helsinki/notification-service-api)
[![codecov](https://codecov.io/gh/City-of-Helsinki/notification-service-api/branch/develop/graph/badge.svg)](https://codecov.io/gh/City-of-Helsinki/notification-service-api)

## Environments

Testing environment:
- https://kuva-notification-service.api.test.hel.ninja/v1/

## Development with Docker

### Prerequisites

If you don't have a `docker compose` subcommand, you may need to install the latest version of Docker. If you have a `docker-compose` command available but no `docker compose`, and `docker-compose` is version 2.x, you need to edit `~/.docker/config.json` in order to add its directory under the `cliPluginsExtraDirs` key (which is an array of directories).

- On macOS, if you have docker installed with homebrew, that directory is `/opt/homebrew/lib/docker/cli-plugins`.
- On Debian Linux, it's in the `/usr/libexec/docker/cli-plugins` directory.
- Although the following example includes both, pick either, or what's appropriate for your distribution.

```json
{
  "cliPluginsExtraDirs": [
    "/opt/homebrew/lib/docker/cli-plugins",
    "/usr/libexec/docker/cli-plugins"
  ]
}
```

### Steps

1. Copy `docker-compose.env.yaml.example` to `docker-compose.env.yaml` and modify it if needed. Be sure that database variables are set (DATABASE_URL and DATABASE_HOST) because those were removed from 'docker-compose.yml' file.

2. Set keycloak hostname

Add the following line to your hosts file (`/etc/hosts` on mac and linux):
    ```
    127.0.0.1       notification-service-keycloak
    ```

If the docker host is on a remote or virtual machine at another interface, use its IP instead of `127.0.0.1`, such as `10.211.55.20`.


3. Run `docker compose up` or `docker compose up --force-recreate --build` if you have made changes, for example,  to environmental variables.

The project is now running at http://notification-service-keycloak:8081.
Keycloak admin interface is running at http://notification-service-keycloak:8180/admin.

The keycloak interface defaults to username "admin" and password "keycloak".

The Keycloak development realm for this project is preconfigured with the name "local-dev". The basic configuration is derived from the file `realm.json`, which is imported during the build process. Realm parameters can be modified through environmental variables in `docker-compose.keycloak.env.yaml` and `docker-compose.env.yaml`. It's essential to ensure that parameters match between the configuration files and the running Keycloak instance to enable the default authentication flow properly.

Additionally, parameters can be set via the Keycloak admin interface. Navigate to the appropriate realm ("local-dev") and review the parameters in the clients, users, and realm settings sections. Keep in mind that any changes made to parameters will be lost if you recreate and rebuild the containers without exporting the realm(s) first.

### Setup the environment configuration file.

Copy `docker-compose.env.yaml.example` to `docker-compose.env.yaml` and modify it if needed.

If you are not running postgresql as a part of the docker compose set, ensure the database variables DATABASE_URL and DATABASE_HOST are set correctly. By default, they point to the default internal hosts of the container network of an unconfigured example.


## Configure the keycloak hostname into /etc/hosts

### TODO: ideally get rid of this step!

Add the following line to your hosts file (`/etc/hosts` on mac and linux):
    ```hosts
    127.0.0.1       notification-service-keycloak
    ```

If the docker host is on a remote or virtual machine at another interface, make ssh tunnels to the virtual machine, forwarding the required ports (8081 and 8180) to your localhost, such as:
    ```shell
    ssh -L8081:localhost:8081 -L8180:localhost:8180 container_host
    ```


## Run the compose file

Execute `docker compose up` in your shell.
Use `docker compose up --force-recreate --build` if you have made changes to environmental variables or have made other untracked changes.

The Keycloak admin interface is running at:
 - http://notification-service-keycloak:8180/admin
 - The keycloak interface defaults to username "admin" and password "keycloak".

 - Default login is admin:adminpass


The Keycloak development realm for this project is preconfigured with the name "local-dev". The basic configuration is derived from the file `realm.json`, which is imported during the build process.

The Realm parameters can be modified through environmental variables in `docker-compose.keycloak.env.yaml` and `docker-compose.env.yaml`.

It's important to ensure matching parameters between the configuration files and the running Keycloak instance. Otherwise, the default authentication flow won't work correctly.

Additional parameters can be configured via the Keycloak admin interface.

Navigate to the appropriate realm ("local-dev") and review the parameters in the clients, users, and realm settings sections.

NOTE: Keep in mind that any changes made to parameters will be lost if you recreate and rebuild the containers without exporting the realm(s) first.



### Configuration
- At the moment the API only integrate with Quriiri SMS gateway, feel free to contribute by creating new sender
- To use the default Quriiri sender, you need to have Quriiri API Key and API URL, then add them to 
`settings.py` or your local `.env`
```python
QURIIRI_API_KEY = <your_quriiri_api_key>
QURIIRI_API_URL = <quriiri_api_url>
``` 
### API Authentication
- The API using default [DRF TokenAuthentication](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication). You need to generate an API token for each client by using CLI
 command

_Note: You have to create API client user first, by login to Django Admin interface using Admin account 
```python
$ python manage.py drf_create_token <username>
```

- After that, include the auth token to the every request to Notification Service. For example:
```curl
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
- [Swagger Hub](https://app.swaggerhub.com/apis-docs/t0mim/NotificationService/1.0.1)

## Keeping Python requirements up to date

1. Install `pip-tools`:

    * `pip install pip-tools`

2. Add new packages to `requirements.in` or `requirements-dev.in`

3. Update `.txt` file for the changed requirements file:

    * `pip-compile requirements.in`
    * `pip-compile requirements-dev.in`

4. If you want to update dependencies to their newest versions, run:

    * `pip-compile --upgrade requirements.in`

5. To install Python requirements run:

    * `pip-sync requirements.txt`

## Code format

This project uses [`black`](https://github.com/ambv/black) for Python code formatting.
We follow the basic config, without any modifications. Basic `black` commands:

* To let `black` do its magic: `black .`
* To see which files `black` would change: `black --check .`

Or you can use [`pre-commit`](https://pre-commit.com/) to quickly format your code before committing.


1. Install `pre-commit` (there are many ways to do but let's use pip as an example):
    * `pip install pre-commit`
2. Set up git hooks from `.pre-commit-config.yaml`, run this command from project root:
    * `pre-commit install`

After that, formatting hooks will run against all changed files before committing
