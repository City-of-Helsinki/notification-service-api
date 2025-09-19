<!-- REMINDER: While updating changelog, also remember to update
the version in notification_service/__init.py__ -->

## [0.6.0](https://github.com/City-of-Helsinki/notification-service-api/compare/notification-service-api-v0.5.5...notification-service-api-v0.6.0) (2025-09-19)


### Features

* Migrate to django-csp 4.0 ([ac20b9f](https://github.com/City-of-Helsinki/notification-service-api/commit/ac20b9f123af785028b1f6bbc38f5cf5adf7c315))


### Bug Fixes

* **dependabot:** Update configuration ([5837a18](https://github.com/City-of-Helsinki/notification-service-api/commit/5837a18218dac5958a9e00323cf8d3978fa124f6))
* Remove deprecated sentry tracing flag ([b8d9658](https://github.com/City-of-Helsinki/notification-service-api/commit/b8d9658f1f3f2929117e4d84ce410f5e9bc24154))


### Dependencies

* Bump django 5.2 and requirements ([e0e2137](https://github.com/City-of-Helsinki/notification-service-api/commit/e0e213746cf3a122e3c67d9a8f8c5ef21ac66a4e))
* Generate hashes for requirements ([3e66283](https://github.com/City-of-Helsinki/notification-service-api/commit/3e66283ad9379014c924d760dca63ef5babd242e))
* Update ruff and pre-commit configurations ([44cb538](https://github.com/City-of-Helsinki/notification-service-api/commit/44cb538577764224f006b7d023761ecd20bd3bcd))
* Upgrade to python 3.12 ([d75bb44](https://github.com/City-of-Helsinki/notification-service-api/commit/d75bb446711c60ad64524b123d65f3dd67e968a4))
* Use psycopg-c instead of psycopg2 ([1a227d4](https://github.com/City-of-Helsinki/notification-service-api/commit/1a227d48e8cdd53038444dc3b4162f74b91c1b80))


### Documentation

* Update README and Docker docs ([e84245b](https://github.com/City-of-Helsinki/notification-service-api/commit/e84245bd6b7fed33002f80330d93a5e477e9858c))

## [0.5.5](https://github.com/City-of-Helsinki/notification-service-api/compare/notification-service-api-v0.5.4...notification-service-api-v0.5.5) (2025-09-10)


### Dependencies

* Bump django from 5.1.11 to 5.1.12 ([8f2bbe6](https://github.com/City-of-Helsinki/notification-service-api/commit/8f2bbe6ff339c9512ceff57808c6f6ec151b86d6))

## [0.5.4](https://github.com/City-of-Helsinki/notification-service-api/compare/notification-service-api-v0.5.3...notification-service-api-v0.5.4) (2025-08-13)


### Bug Fixes

* Add missing migration ([61662fc](https://github.com/City-of-Helsinki/notification-service-api/commit/61662fca51960fa5aaf735b815a3f9f50fe2de2f))
* Database password & refactor pipelines ([#99](https://github.com/City-of-Helsinki/notification-service-api/issues/99)) ([da029b8](https://github.com/City-of-Helsinki/notification-service-api/commit/da029b816a5469edeb191e3122bc37233f95b79f))


### Dependencies

* Bump urllib3 from 2.2.3 to 2.5.0 ([6cd6403](https://github.com/City-of-Helsinki/notification-service-api/commit/6cd64032ccd8b31fe4b116e5ee9ec7aa501e924b))

## [0.5.3](https://github.com/City-of-Helsinki/notification-service-api/compare/notification-service-api-v0.5.2...notification-service-api-v0.5.3) (2025-06-11)


### Dependencies

* Bump django from 5.1.10 to 5.1.11 ([981470b](https://github.com/City-of-Helsinki/notification-service-api/commit/981470bddf621914de46c55fdc16dfc123b9cee0))
* Bump requests from 2.32.3 to 2.32.4 ([462d835](https://github.com/City-of-Helsinki/notification-service-api/commit/462d835f78d9f388b1750abff0e66fed721a8608))

## [0.5.2](https://github.com/City-of-Helsinki/notification-service-api/compare/notification-service-api-v0.5.1...notification-service-api-v0.5.2) (2025-06-09)


### Dependencies

* Bump django from 5.1.9 to 5.1.10 ([0cd486a](https://github.com/City-of-Helsinki/notification-service-api/commit/0cd486aebaa1f671166e5c998178a9d0cb6b256f))

## [0.5.1](https://github.com/City-of-Helsinki/notification-service-api/compare/notification-service-api-v0.5.0...notification-service-api-v0.5.1) (2025-05-23)


### Dependencies

* Bump cryptography from 43.0.3 to 44.0.1 ([b6c510d](https://github.com/City-of-Helsinki/notification-service-api/commit/b6c510d41f4d1709c1c17612ac670fb619334983))
* Bump django from 5.1.2 to 5.1.9 ([25dff55](https://github.com/City-of-Helsinki/notification-service-api/commit/25dff55907509df7d8a519f6c3e9e76298ff6f3f))
* Bump python-jose from 3.3.0 to 3.4.0 ([3dc1b49](https://github.com/City-of-Helsinki/notification-service-api/commit/3dc1b497ba5d5b83212add3c3366d2f581370899))

## [0.5.0](https://github.com/City-of-Helsinki/notification-service-api/compare/notification-service-api-v0.4.1...notification-service-api-v0.5.0) (2024-12-02)


### Features

* Add prune_(delivery_log|django_admin_log) management commands ([76e1450](https://github.com/City-of-Helsinki/notification-service-api/commit/76e1450dce6d9d99f889ebcef3229a6a6d1ab20a))
* Add Table of Contents to all Markdown files except CHANGELOG.md ([c15e08c](https://github.com/City-of-Helsinki/notification-service-api/commit/c15e08c15eb2f02b5426ed29512beedf4464cd90))
* **auditlog:** Add "user_id" field to audit actor ([a4af758](https://github.com/City-of-Helsinki/notification-service-api/commit/a4af758bdb8a4c7954fbabe202753a3770ec041d))
* **auditlog:** Add a management command to prune the audit logs ([186b1bc](https://github.com/City-of-Helsinki/notification-service-api/commit/186b1bc1af152e6fb48b0553b698a2dcb9a4bda1))
* **auditlog:** Add audit log admin view mixin ([ccb9979](https://github.com/City-of-Helsinki/notification-service-api/commit/ccb9979d4826810fbe3ee75f447e78769b0c5d85))
* **auditlog:** Add AuditLogManager and AuditLogQuerySet ([51ee0a2](https://github.com/City-of-Helsinki/notification-service-api/commit/51ee0a2b10c34bb3e4cd420a0173a7763c508f77))
* **auditlog:** Add dry_run option to prune audit logs command ([1e39326](https://github.com/City-of-Helsinki/notification-service-api/commit/1e3932622f995d1ef2c4cb3f04f118673ad6e793))
* **auditlog:** Add is_sent option to prune audit logs command ([c3d2482](https://github.com/City-of-Helsinki/notification-service-api/commit/c3d2482d759ea809a5ba3f929c0b14d2e16707a8))
* **auditlog:** Add model_name in the audit log target ([33af4b9](https://github.com/City-of-Helsinki/notification-service-api/commit/33af4b947c7b76a2d6e22d2e449c88f1a69e1021))
* **auditlog:** Extend DeliveryLog admin view with audit logging ([f53ca5b](https://github.com/City-of-Helsinki/notification-service-api/commit/f53ca5b80fbdadb55e917552391134fc9664c140))
* **auditlog:** Install and init audit_log app ([f5e95c7](https://github.com/City-of-Helsinki/notification-service-api/commit/f5e95c7ca152f4926c71229a31e631787be4cdcc))
* **auditlog:** Message columns and filters to admin list view ([2c43e4f](https://github.com/City-of-Helsinki/notification-service-api/commit/2c43e4f69ac219b5bca6d798748bcc317da2787a))
* **auditlog:** Start writing the object states to audit log ([92384e4](https://github.com/City-of-Helsinki/notification-service-api/commit/92384e4993be1c575e04789200d9ea0960b6d2f9))
* **auditlog:** Store object states and diffs to audit event target ([ad8454c](https://github.com/City-of-Helsinki/notification-service-api/commit/ad8454ca49a13e6899c7358e8c702c6a663e023a))
* **auditlog:** Write audit log from delivery log api actions ([d5038a5](https://github.com/City-of-Helsinki/notification-service-api/commit/d5038a56e7f7e1ef3b1127a4b55c7ae7cc0d4e67))
* Delivery log admin search from report field ([8fd461e](https://github.com/City-of-Helsinki/notification-service-api/commit/8fd461e7bdb92aba95d5ac4ed06c611a9e060b59))
* Filter message logs with created at date ([3bf7e28](https://github.com/City-of-Helsinki/notification-service-api/commit/3bf7e2819519319d23f526706535d04c69505030))
* Improve user admin view ([a8e7d23](https://github.com/City-of-Helsinki/notification-service-api/commit/a8e7d23eafeb2fa613637339edb98ca441ae0bb3))
* Install and configure django-csp ([12875c4](https://github.com/City-of-Helsinki/notification-service-api/commit/12875c4bdce988011ca3885f70ff202cedc4ab7e))
* Message logs admin default ordering set to descending created at ([fd5a3d4](https://github.com/City-of-Helsinki/notification-service-api/commit/fd5a3d4420c776edeb43668cbdbfc03c201539c1))
* Message logs admin filter with status ([d9fe2c1](https://github.com/City-of-Helsinki/notification-service-api/commit/d9fe2c1a96ea04970ca9ea295ef4184974ba66ea))
* Prune audit/delivery/Django admin logs using uwsgi cron at night ([66cf503](https://github.com/City-of-Helsinki/notification-service-api/commit/66cf503e7365bce15ed9ff4c66d9b0d4c007d606))
* Search message logs with user email ([5687125](https://github.com/City-of-Helsinki/notification-service-api/commit/5687125f28f030d51c7bbbc63e9b7386539fe682))
* Validate input of send message and filter invalid phone numbers ([b8a8485](https://github.com/City-of-Helsinki/notification-service-api/commit/b8a8485675da5595cbb5ed5c0d2123c076ba760e))
* Whitelist only the auth service for CORS ([889e7a4](https://github.com/City-of-Helsinki/notification-service-api/commit/889e7a4fddda00b73bc0e49ff2f4cd8674f80f5d))


### Bug Fixes

* **auditlog:** Audit log model admin mixin save model operation value ([f45dda1](https://github.com/City-of-Helsinki/notification-service-api/commit/f45dda1ae61effa488bc159c2ed19aab37ce8862))
* **auditlog:** Write readlog only of current admin list page objects ([f140128](https://github.com/City-of-Helsinki/notification-service-api/commit/f140128ed8aa0960271d8cf581abfbb1f774b241))
* Hot reload when using docker compose by using .:/app volume mapping ([90d6f28](https://github.com/City-of-Helsinki/notification-service-api/commit/90d6f28908c347705b2d8aea3ab1e43a32d4e469))
* Remove cronjobs from uwsgi.ini, OpenShift is wanted for cronjobs ([5979301](https://github.com/City-of-Helsinki/notification-service-api/commit/5979301d92a06cf9d306b6577d48a8a36f294cb2))


### Documentation

* **auditlog:** Add a reference to structued log transfer ([a4ae0af](https://github.com/City-of-Helsinki/notification-service-api/commit/a4ae0af059a060a5f4ecd34ae577c58ac510b923))
* **auditlog:** Audit log object state storing ([ba07f41](https://github.com/City-of-Helsinki/notification-service-api/commit/ba07f41540999e2c007de4250dddb92f929e616a))
* **auditlog:** Init readme for audit log ([ea0a9ff](https://github.com/City-of-Helsinki/notification-service-api/commit/ea0a9ff077f9e7b2540588761c5d7f6c2c5c2355))

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
