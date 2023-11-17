from django.urls import path

from . import views

urlpatterns = [
    path("message/send", views.send_message, name="send_message"),
    path("message/<id>", views.get_delivery_log, name="get_message"),
    path(
        "message/webhook/<id>",
        views.delivery_log_webhook,
        name="delivery_log_webhook",
    ),
]
