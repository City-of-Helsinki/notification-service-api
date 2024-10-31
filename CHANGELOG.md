<!-- REMINDER: While updating changelog, also remember to update
the version in notification_service/__init.py__ -->

## [0.4.1](https://github.com/City-of-Helsinki/notification-service-api/compare/notification-service-api-v0.4.0...notification-service-api-v0.4.1) (2024-10-31)


### Bug Fixes

* Add DjangoIntegration to Sentry settings ([6438ca0](https://github.com/City-of-Helsinki/notification-service-api/commit/6438ca0605c045c23604aa9f586b005ef3b5b044))

## [0.4.0](https://github.com/City-of-Helsinki/notification-service-api/compare/notification-service-api-v0.3.3...notification-service-api-v0.4.0) (2024-10-30)


### Features

* Add build and release information to the readiness probe ([f76cfe3](https://github.com/City-of-Helsinki/notification-service-api/commit/f76cfe32a050472b36874448640911895721ed38))

## [0.3.3](https://github.com/City-of-Helsinki/notification-service-api/compare/notification-service-api-v0.3.2...notification-service-api-v0.3.3) (2024-10-30)


### Bug Fixes

* Add project in pyproject.toml to fix release please versioning ([471a296](https://github.com/City-of-Helsinki/notification-service-api/commit/471a2964a94f55b50a2e3b0191ff0bb63a2c9b71))
* **release:** Set release version to Django project ([3951bf2](https://github.com/City-of-Helsinki/notification-service-api/commit/3951bf2f2d95f3661dcf967888eec2bdeb727ed4))

## [0.3.2](https://github.com/City-of-Helsinki/notification-service-api/compare/notification-service-api-v0.3.1...notification-service-api-v0.3.2) (2024-10-30)


### Bug Fixes

* **release:** Set release version to Django project ([5463ad2](https://github.com/City-of-Helsinki/notification-service-api/commit/5463ad2a44992855d4e3f1bfc1562580bf88e0ae))


### Documentation

* Releasing with release-please process and deploying ([a336ccb](https://github.com/City-of-Helsinki/notification-service-api/commit/a336ccb5ecb2b7eeb849d102bd6aacdc326b2207))

## [0.3.1](https://github.com/City-of-Helsinki/notification-service-api/compare/notification-service-api-v0.3.0...notification-service-api-v0.3.1) (2024-10-29)


### Bug Fixes

* **release:** Trigger a new release with release-please ([3488748](https://github.com/City-of-Helsinki/notification-service-api/commit/3488748871ec9ec3f7ec7500b4f1d2b2483eb22a))

## [0.3.0](https://github.com/City-of-Helsinki/notification-service-api/compare/notification-service-api-v0.2.0...notification-service-api-v0.3.0) (2024-10-29)


### Features

* **deps:** Remove unused dependency to django-ilmoitin ([4a082a9](https://github.com/City-of-Helsinki/notification-service-api/commit/4a082a93f649eeee0c8e16be15ef58dfc18cac17))
* Healthz-endpoint checks the database connection ([0e88293](https://github.com/City-of-Helsinki/notification-service-api/commit/0e882939a88c182c4317b0e03b6557ac61a7a2ea))


### Bug Fixes

* Cache directory permission errors when running ruff & pytest ([cd3902d](https://github.com/City-of-Helsinki/notification-service-api/commit/cd3902d11eff6e40f10189f161ec5e55e0d9331b))
* Chained even more RUNs to make SonarCloud happy. ([a4d51ea](https://github.com/City-of-Helsinki/notification-service-api/commit/a4d51ea12fee5182d4afb5fad2278c712fac35d3))
* Compatibility with podman 5.2.3 ([3ed0300](https://github.com/City-of-Helsinki/notification-service-api/commit/3ed0300b7822428c2a379aa8ad7c99bf58f741ec))
* Manage.py can't be assumed to be executable. ([a12ea37](https://github.com/City-of-Helsinki/notification-service-api/commit/a12ea373ff9d96f771e3980926db762b53208c52))
* The 'version' attribute is deprecated ([e429802](https://github.com/City-of-Helsinki/notification-service-api/commit/e429802078926bc10d033b25fd0f818338c4a310))
* The entrypoint script calls manage.py, therefore it can't exist before /app. ([ded8a54](https://github.com/City-of-Helsinki/notification-service-api/commit/ded8a540db46c74ce701281c2d708ff5934d672f))


### Documentation

* Added description of what the project is about. ([910f8c0](https://github.com/City-of-Helsinki/notification-service-api/commit/910f8c0eb82b772f3ab4f95a06c22d9adca96a64))
* Bringing README up to date and adding details, as well as fixmes. ([6965dd6](https://github.com/City-of-Helsinki/notification-service-api/commit/6965dd6d5f21b98fc1b18e10f733f75a346e4bf3))
* Code formatting with ruff ([b322767](https://github.com/City-of-Helsinki/notification-service-api/commit/b322767cd486c1e2431cf63d2ce808b41a1e2b4c))
* Docker-compose is still by default a separate command ([81b63b6](https://github.com/City-of-Helsinki/notification-service-api/commit/81b63b6bc956b0516eb19d0d17947c724c819f30))
* Notes about docker-compose configuration and minor fixes. ([7e5fca5](https://github.com/City-of-Helsinki/notification-service-api/commit/7e5fca52067407b7b33e24bdd10874bef810bf95))
* Separated instructions without docker; possibly outdated. ([9930279](https://github.com/City-of-Helsinki/notification-service-api/commit/99302798b4d446551cd63d3787d6bc3d7020713d))

## [0.2.0] - 26 Mar 2024

### Added

- Keycloak integration

## [0.1.0] - 5 Oct 2020

### Added

- Notification REST API:
  - Add API token authentication
  - Add API to send SMS to phone numbers
  - Add delivery log endpoint to receive delivery report from webhook
  - Add API to query delivery report by message UUID

[Unreleased]: https://github.com/City-of-Helsinki/notificartion-service/compare/release-v0.1.0...HEAD
[0.1.0]: https://github.com/City-of-Helsinki/notification-service/releases/tag/release-v0.1.0
