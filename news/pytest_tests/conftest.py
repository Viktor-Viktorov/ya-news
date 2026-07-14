from datetime import date

import pytest
from django.test.client import Client

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='author')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='not_author')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок новости',
        text='Текст новости',
        date=date.today(),
    )


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def news_id_for_args(news):
    return (news.pk,)


@pytest.fixture
def comment_id_for_args(comment):
    return (comment.pk,)


@pytest.fixture
def form_data():
    return {'text': 'Новый текст комментария'}
