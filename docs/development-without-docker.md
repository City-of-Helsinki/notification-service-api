# NOTE: These instructions are not verified being up to date.

Please refer to the [main README](/README.md) for the latest instructions.

## Development without Docker

Prerequisites:

- PostgreSQL 13
- Python 3.11
- Keycloak

### Installing Python requirements

- Run `pip install -r requirements.txt`
- Run `pip install -r requirements-dev.txt` (development requirements)

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

- Create `.env` file: `touch .env` or make a copy of `.env.example`
- Set the `DEBUG` environment variable to `1`.
- Run `python manage.py migrate`
- Run `python manage.py runserver localhost:8081`
- The project is now running at http://localhost:8081
- [When Keycloak has been started](#original-keycloak), it is running at http://localhost:8180 and at http://notification-service-keycloak:8180 (if hostname is set)
