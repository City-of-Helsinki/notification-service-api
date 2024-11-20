import factory

from api.models import DeliveryLog
from users.factories import UserFactory


class DeliveryLogFactory(factory.django.DjangoModelFactory):
    report = factory.Faker("pystr", max_chars=255)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = DeliveryLog
