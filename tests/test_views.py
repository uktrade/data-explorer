from django.shortcuts import reverse

import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url',
    (
        'explorer_index',
        'explorer_logs',
        'query_create',
        'explorer_playground',
    ),
)
def test_view(authenticated_client, url):
    response = authenticated_client.get(reverse(url))
    assert response.status_code == 200
