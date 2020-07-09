import factory
from api.models import DeliveryLog
from users.models import User


class DeliveryLogFactory(factory.django.DjangoModelFactory):
    payload = factory.Faker("pystr", max_chars=255)
    user = factory.SubFactory(User)

    class Meta:
        model = DeliveryLog
