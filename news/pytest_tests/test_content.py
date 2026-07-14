from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from pytest_lazyfixture import lazy_fixture as lf

from news.forms import CommentForm
from news.models import Comment, News

pytestmark = pytest.mark.django_db


@pytest.fixture
def many_news():
    today = datetime.today()
    return News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Какой-то текст.',
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def many_comments(news, author):
    now = timezone.now()
    comments = []
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments.append(comment)
    return comments


def test_news_count(client, many_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']

    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, many_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)

    assert all_dates == sorted_dates


@pytest.mark.parametrize(
    'parametrized_client',
    (
        lf('client'),
        lf('not_author_client'),
    ),
)
def test_news_in_home_page_for_different_users(news, parametrized_client):
    url = reverse('news:home')
    response = parametrized_client.get(url)
    object_list = response.context['object_list']

    assert news in object_list


def test_comments_order(client, news, many_comments):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)

    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)

    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)

    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)

    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
