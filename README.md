# Notification service API


[![status](https://travis-ci.com/City-of-Helsinki/notification-service-api.svg)](https://github.com/City-of-Helsinki/notification-service-api)
[![codecov](https://codecov.io/gh/City-of-Helsinki/notification-service-api/branch/develop/graph/badge.svg)](https://codecov.io/gh/City-of-Helsinki/notification-service-api)

## Environments

Testing environment:
- https://kuva-notification-service.api.test.hel.ninja/v1/

## Development with Docker

1. Copy `docker-compose.env.yaml.example` to `docker-compose.env.yaml` and modify it if needed. Be sure that database variables are set (DATABASE_URL and DATABASE_HOST) because those were removed from 'docker-compose.yml' file.

2. Set keycloak hostname

   Add the following line to your hosts file (`/etc/hosts` on mac and linux):
    ```
    127.0.0.1       notification-service-keycloak
    ```

3. Run `docker compose up` or `docker compose up --force-recreate --build` if you have made changes, for example,  to environmental variables.

The project is now running at http://localhost:8081.
Keycloak admin interface is running at http://notification-service-keycloak:8180/admin.

The Keycloak development realm for this project is preconfigured with the name "local-dev". The basic configuration is derived from the file `realm.json`, which is imported during the build process. Realm parameters can be modified through environmental variables in `docker-compose.keycloak.env.yaml` and `docker-compose.env.yaml`. It's essential to ensure that parameters match between the configuration files and the running Keycloak instance to enable the default authentication flow properly.

Additionally, parameters can be set via the Keycloak admin interface. Navigate to the appropriate realm ("local-dev") and review the parameters in the clients, users, and realm settings sections. Keep in mind that any changes made to parameters will be lost if you recreate and rebuild the containers without exporting the realm(s) first.

## Development without Docker

Prerequisites:

* PostgreSQL 12
* Python 3.9
* Keycloak 

### Installing Python requirements

* Run `pip install -r requirements.txt`
* Run `pip install -r requirements-dev.txt` (development requirements)

### Database

To setup a database compatible with default database settings:

Create user and database

    sudo -u postgres createuser -P -R -S notification_service  # use password `notification_service`
    sudo -u postgres createdb -O notification_service notification_service

Allow user to create test database

    sudo -u postgres psql -c "ALTER USER notification_service CREATEDB;"
    
### Keycloak

#### Helsinki Keycloak theme

Clone Helsinki Keycloak theme if needed.
    
    git clone git@github.com:City-of-Helsinki/helsinki-keycloak-theme.git

Follow the instructions on the following website to setup and start this standalone version of Keycloak (Helsinki theme). https://github.com/City-of-Helsinki/helsinki-keycloak-theme

#### Original Keycloak

After setting up the theme, start the "original" Keycloak container using the provided script below. Keep in mind that the included volumes reference the Helsinki theme and development realm parameters from the Notification service project.

```
docker run --name notification-service-keycloak \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=keycloak \
  -v /path/to/notification_service/keycloak/realm.json:/opt/keycloak/data/import/realm.json \
  -v /path/to/helsinki-keycloak-theme/helsinki:/opt/keycloak/themes/helsinki \
  --network=helsinki \
  quay.io/keycloak/keycloak \
  start-dev \
  --http-port=8180 \
  --spi-theme-static-max-age=-1 \
  --spi-theme-cache-themes=false \
  --spi-theme-cache-templates=false \
  --import-realm
```

When the container have started, you can copy Helsinki theme. Please ensure that both the original and Helsinki theme Keycloak containers are running simultaneously.

    docker cp /path/to/helsinki-keycloak-theme/helsinki/. keycloak:/opt/keycloak/themes/helsinki

Remember to set Keycloak hostname as instructed earlier ([Development with docker -> Set hostname](#development-with-docker)).

### Daily running, Debugging

* Create `.env` file: `touch .env` or make a copy of `.env.example` 
* Set the `DEBUG` environment variable to `1`.
* Run `python manage.py migrate`
* Run `python manage.py runserver localhost:8081`
* The project is now running at http://localhost:8081
* [When Keycloak has been started](#original-keycloak), it is running at http://localhost:8180 and at http://notification-service-keycloak:8180 (if hostname is set)

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
