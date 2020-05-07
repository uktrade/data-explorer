import pytest

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model


def pytest_sessionstart(session):
    databases_to_enable = {'default', 'datasets'}
    TransactionTestCase.databases = databases_to_enable
    TestCase.databases = databases_to_enable


@pytest.fixture
def authenticated_client(client, user):
    client.force_login(user)
    yield client


@pytest.fixture
def user():
    yield get_user_model().objects.create(
        email='test@test.com',
        is_staff=False,
        is_superuser=False
    )
