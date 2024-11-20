# Notification service API

[![status](https://travis-ci.com/City-of-Helsinki/notification-service-api.svg)](https://github.com/City-of-Helsinki/notification-service-api)
[![codecov](https://codecov.io/gh/City-of-Helsinki/notification-service-api/branch/develop/graph/badge.svg)](https://codecov.io/gh/City-of-Helsinki/notification-service-api)

The Notification service API is a Django REST Framework API for sending notifications via SMS, email, and push notifications. The API is designed to be used by other services to send notifications to users.

## Table of Contents
<!-- TOC start (generated with https://github.com/derlin/bitdowntoc) -->

- [Service environments](#service-environments)
- [Prerequisites](#prerequisites)
   * [Docker](#docker)
   * [Docker Compose](#docker-compose)
- [Dependencies](#dependencies)
   * [Python](#python)
   * [PostgreSQL](#postgresql)
   * [Keycloak](#keycloak)
   * [Quriiri](#quriiri)
   * [Other](#other)
- [Getting started](#getting-started)
   * [Setup the environment configuration file.](#setup-the-environment-configuration-file)
   * [Configure the keycloak hostname into /etc/hosts](#configure-the-keycloak-hostname-into-etchosts)
      + [TODO: ideally get rid of this step!](#todo-ideally-get-rid-of-this-step)
   * [Run the compose file](#run-the-compose-file)
   * [Inspect the services.](#inspect-the-services)
      + [The Keycloak admin interface should be available at:](#the-keycloak-admin-interface-should-be-available-at)
      + [The API should be available at:](#the-api-should-be-available-at)
- [About Keycloak](#about-keycloak)
   * [Configuration of additional parameters](#configuration-of-additional-parameters)
   * [Configuration](#configuration)
   * [API Authentication](#api-authentication)
- [API Documentation](#api-documentation)
   * [Phone Number Processing](#phone-number-processing)
   * [TODO: FIXME!](#todo-fixme)
- [Keeping Python requirements up to date](#keeping-python-requirements-up-to-date)
- [Code formatting](#code-formatting)
- [Releases, changelogs and deployments](#releases-changelogs-and-deployments)
   * [Conventional Commits](#conventional-commits)
   * [Releasable units](#releasable-units)
   * [Configuration](#configuration-1)
   * [Troubleshoting release-please](#troubleshoting-release-please)
      + [Fix merge conflicts by running release-please -action manually](#fix-merge-conflicts-by-running-release-please--action-manually)
   * [Deployments](#deployments)

<!-- TOC end -->

## Service environments

The environments:

- Testing; https://kuva-notification-service.api.test.hel.ninja/v1/: The environment that is built and deployed every time when a new commit to master code branch is pushed.
- Staging; https://kuva-notification-service.api.stage.hel.ninja/v1/: A released version (triggered with tag) is first deployed to the staging server, where the version can be tested before deploying it to production.
- Production; https://kuva-notification-service.api.hel.fi/v1/.

NOTE: Also a new development environment is created with a dynamic URL everytime when a new pull request is created. The URL will be posted as automatically as a comment in the pull request.

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

### Phone Number Processing

This application provides tools for validating and formatting phone numbers using the [phonenumberslite](https://pypi.org/project/phonenumberslite/) library. It's designed to handle a variety of phone number formats and ensure accurate processing.

Features:

- **Phone Number Validation:** Accurately validates phone numbers using the `phonenumberslite` library, ensuring they are in a valid format and potentially even checking their reachability. The phone number parser region is set to "FI".
- **Invalid Number Filtering:** Identifies and filters out invalid phone numbers, including those with invalid characters or formats.
- **Letter Filtering:** Specifically handles and rejects phone numbers containing letters to prevent unintended conversions.
- **Internationalization:** Converts phone numbers to international format for consistency and global compatibility.
- **Error Handling:** Includes robust error handling to gracefully manage invalid input and provide informative logging for debugging.

> The phone numbers that are set as destination but are not valid, are filtered out from the list of recipients.

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

ruff format # Format all files in the current directory.
ruff format path/to/code/ # Format all files in `path/to/code` (and any subdirectories).
ruff format path/to/file.py # Format a single file.

```

> Similar to Black, running ruff format /path/to/file.py will format the given file or directory in-place, while ruff format --check /path/to/file.py will avoid writing any formatted files back, and instead exit with a non-zero status code upon detecting any unformatted files.

To run the Ruff Linter use `ruff check`.

> `ruff check` is the primary entrypoint to the Ruff linter. It accepts a list of files or directories, and lints all discovered Python files, optionally fixing any fixable errors:

```

ruff check # Lint all files in the current directory.
ruff check --fix # Lint all files in the current directory, and fix any fixable errors.
ruff check --watch # Lint all files in the current directory, and re-lint on change.
ruff check path/to/code/ # Lint all files in `path/to/code` (and any subdirectories).

```

1. Install `pre-commit` (there are many ways to do but let's use pip as an example):
   - `pip install pre-commit`
2. Set up git hooks from `.pre-commit-config.yaml`, run this command from project root:
   - `pre-commit install`

After that, formatting hooks will run against all changed files before committing

## Releases, changelogs and deployments

The used environments are listed in [Service environments](#service-environments).

The application uses automatic semantic versions and is released using [Release Please](https://github.com/googleapis/release-please).

> Release Please is a GitHub Action that automates releases for you. It will create a GitHub release and a GitHub Pull Request with a changelog based on conventional commits.

Each time you merge a "normal" pull request, the release-please-action will create or update a "Release PR" with the changelog and the version bump related to the changes (they're named like `release-please--branches--master--components--notification-service-api`).

To create a new release for an app, this release PR is merged, which creates a new release with release notes and a new tag. This tag will be picked by Azure pipeline and trigger a new deployment to staging. From there, the release needs to be manually released to production.

When merging release PRs, make sure to use the "Rebase and merge" (or "Squash and merge") option, so that Github doesn't create a merge commit. All the commits must follow the conventional commits format. This is important, because the release-please-action does not work correctly with merge commits (there's an open issue you can track: [Chronological commit sorting means that merged PRs can be ignored ](https://github.com/googleapis/release-please/issues/1533)).

See [Release Please Implementation Design](https://github.com/googleapis/release-please/blob/main/docs/design.md) for more details.

And all docs are available here: [release-please docs](https://github.com/googleapis/release-please/tree/main/docs).

### Conventional Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) to ensure that the changelogs are generated correctly.

### Releasable units

Release please goes through commits and tries to find "releasable units" using commit messages as guidance - it will then add these units to their respective release PR's and figures out the version number from the types: `fix` for patch, `feat` for minor, `feat!` for major. None of the other types will be included in the changelog. So, you can use for example `chore` or `refactor` to do work that does not need to be included in the changelog and won't bump the version.

### Configuration

The release-please workflow is located in the [release-please.yml](./.github/workflows/release-please.yml) file.

The configuration for release-please is located in the [release-please-config.json](./release-please-config.json) file.
See all the options here: [release-please docs](https://github.com/googleapis/release-please/blob/main/docs/manifest-releaser.md).

The manifest file is located in the [release-please-manifest.json](./.release-please-manifest.json) file.

When adding a new app, add it to both the [release-please-config.json](./release-please-config.json) and [release-please-manifest.json](./.release-please-manifest.json) file with the current version of the app. After this, release-please will keep track of versions with [release-please-manifest.json](./.release-please-manifest.json).

### Troubleshoting release-please

If you were expecting a new release PR to be created or old one to be updated, but nothing happened, there's probably one of the older release PR's in pending state or action didn't run.

1. Check if the release action ran for the last merge to main. If it didn't, run the action manually with a label.
2. Check if there's any open release PR. If there is, the work is now included on this one (this is the normal scenario).
3. If you do not see any open release PR related to the work, check if any of the closed PR's are labeled with `autorelease: pending` - ie. someone might have closed a release PR manually. Change the closed PR's label to `autorelease: tagged`. Then go and re-run the last merge workflow to trigger the release action - a new release PR should now appear.
4. Finally check the output of the release action. Sometimes the bot can't parse the commit message and there is a notification about this in the action log. If this happens, it won't include the work in the commit either. You can fix this by changing the commit message to follow the [Conventional Commits](https://www.conventionalcommits.org/) format and rerun the action.

**Important!** If you have closed a release PR manually, you need to change the label of closed release PR to `autorelease: tagged`. Otherwise, the release action will not create a new release PR.

**Important!** Extra label will force release-please to re-generate PR's. This is done when action is run manually with prlabel -option

Sometimes there might be a merge conflict in release PR - this should resolve itself on the next push to main. It is possible run release-please action manually with label, it should recreate the PR's. You can also resolve it manually, by updating the [release-please-manifest.json](./.release-please-manifest.json) file.

#### Fix merge conflicts by running release-please -action manually

1. Open [release-please github action](https://github.com/City-of-Helsinki/notification-service-api/actions/workflows/release-please.yml)
2. Click **Run workflow**
3. Check Branch is **master**
4. Leave label field empty. New label is not needed to fix merge issues
5. Click **Run workflow** -button

There's also a CLI for debugging and manually running releases available for release-please: [release-please-cli](https://github.com/googleapis/release-please/blob/main/docs/cli.md)

### Deployments

When a Release-Please pull request is merged and a version tag is created (or a proper tag name for a commit is manually created), this tag will be picked by Azure pipeline, which then triggers a new deployment to staging. From there, the deployment needs to be manually approved to allow it to proceed to the production environment.

The tag name is defined in the [azure-pipelines-notification-service-api-release.yml](./azure-pipelines-notification-service-api-release.yml).

```

```
