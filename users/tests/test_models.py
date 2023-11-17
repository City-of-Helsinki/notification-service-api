import pytest

from users.factories import UserFactory
from users.models import User


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


def test_api_user_models():
    UserFactory()
    assert User.objects.count() == 1
