"""notification_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.utils.translation import gettext

from common.utils import get_api_version
from custom_health_checks.views import HealthCheckJSONView
from notification_service import __version__, settings

admin.site.index_title = " ".join(
    [gettext("Notification service API"), get_api_version()]
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("pysocial/", include("social_django.urls", namespace="social")),
    path("helauth/", include("helusers.urls")),
    path("v1/", include("api.urls")),
]


#
# Kubernetes liveness & readiness probes
#
def readiness(*args, **kwargs):
    response_json = {
        "status": "ok",
        "release": settings.APP_RELEASE,
        "packageVersion": __version__,
        "commitHash": settings.REVISION,
        "buildTime": settings.APP_BUILD_TIME.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
    }
    return JsonResponse(response_json, status=200)


urlpatterns += [
    path(r"healthz", HealthCheckJSONView.as_view(), name="healthz"),
    path(r"readiness", readiness),
]
