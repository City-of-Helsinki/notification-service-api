import factory
from django.contrib.auth import get_user_model
from users.models import ApiUser


class UserFactory(factory.django.DjangoModelFactory):
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Faker("user_name")
    email = factory.Faker("email")

    class Meta:
        model = get_user_model()


class ApiUserFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    api_key = factory.Faker("pystr", max_chars=64)

    class Meta:
        model = ApiUser
