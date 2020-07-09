from django.urls import include, path

from . import views

urlpatterns = [
    path("message/", views.send_message),
    path("message/<uuid>", views.get_delivery_log),
    path("message/webhook/<uuid>", views.delivery_log_webhook),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
