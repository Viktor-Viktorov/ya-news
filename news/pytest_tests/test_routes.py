from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', lf('news_id_for_args')),
        ('users:login', None),
        ('users:signup', None),
    ),
)
def test_pages_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


def test_logout_availability_for_anonymous_user(client):
    url = reverse('users:logout')
    response = client.post(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', lf('news_id_for_args')),
    ),
)
def test_pages_availability_for_auth_user(not_author_client, name, args):
    url = reverse(name, args=args)
    response = not_author_client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_comment_pages_availability_for_different_users(
    parametrized_client,
    name,
    comment_id_for_args,
    expected_status,
):
    url = reverse(name, args=comment_id_for_args)
    response = parametrized_client.get(url)

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lf('comment_id_for_args')),
        ('news:delete', lf('comment_id_for_args')),
    ),
)
def test_redirects(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)

    assertRedirects(response, expected_url)
