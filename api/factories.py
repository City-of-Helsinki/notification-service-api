import factory
from api.models import DeliveryLog
from users.factories import ApiUserFactory


class DeliveryLogFactory(factory.django.DjangoModelFactory):
    payload = factory.Faker("pystr", max_chars=255)
    api_user = factory.SubFactory(ApiUserFactory)

    class Meta:
        model = DeliveryLog
