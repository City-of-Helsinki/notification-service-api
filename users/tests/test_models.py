import pytest
from users.factories import ApiUserFactory
from users.models import ApiUser, User


@pytest.fixture(autouse=True)
def autouse_db(db):
    pass


def test_api_user_models():
    ApiUserFactory()
    assert ApiUser.objects.count() == 1
    assert User.objects.count() == 1
