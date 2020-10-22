# Notification service API


[![status](https://travis-ci.com/City-of-Helsinki/notification-service-api.svg)](https://github.com/City-of-Helsinki/notification-service-api)
[![codecov](https://codecov.io/gh/City-of-Helsinki/notification-service-api/branch/develop/graph/badge.svg)](https://codecov.io/gh/City-of-Helsinki/notification-service-api)


## Environments
Production environment:
- https://api.hel.fi/notification-service/v1

Testing environment:
- https://notification-service-api.test.kuva.hel.ninja/v1

## Development with Docker

1. Copy `docker-compose.env.yaml.example` to `docker-compose.env.yaml` and modify it if needed.

2. Run `docker-compose up`

The project is now running at [localhost:8081](http://localhost:8081)

## Development without Docker

Prerequisites:

* PostgreSQL 10
* Python 3.7

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
    

### Daily running, Debugging

* Create `.env` file: `touch .env` or make a copy of `.env.example` 
* Set the `DEBUG` environment variable to `1`.
* Run `python manage.py migrate`
* Run `python manage.py runserver localhost:8081`
* The project is now running at [localhost:8081](http://localhost:8081)

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
$ python manager.py drf_create_token <username>
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
- [Swagger Hub](https://app.swaggerhub.com/apis-docs/t0mim/NotificationService/1.0.0)

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

## Contact infomation

@quyenlq