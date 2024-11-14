import factory
from django.contrib.admin.models import ACTION_FLAG_CHOICES, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from api.models import DeliveryLog
from users.factories import UserFactory


class DeliveryLogFactory(factory.django.DjangoModelFactory):
    report = factory.Faker("pystr", max_chars=255)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = DeliveryLog


class LogEntryFactory(factory.django.DjangoModelFactory):
    action_time = factory.LazyFunction(timezone.now)
    user = factory.SubFactory(UserFactory)
    content_type = factory.LazyFunction(
        lambda: ContentType.objects.get_for_model(LogEntry)
    )
    object_id = factory.Faker("uuid4")
    object_repr = factory.Faker("text", max_nb_chars=200)
    action_flag = factory.Faker(
        "random_element", elements=[value for value, _ in ACTION_FLAG_CHOICES]
    )
    change_message = factory.Faker("text")

    class Meta:
        model = LogEntry
