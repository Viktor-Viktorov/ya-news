from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_user_can_create_comment(author_client, author, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)

    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.news == news
    assert new_comment.author == author


def test_anonymous_user_cant_create_comment(client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'

    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {
        'text': f'Какой-то текст, {BAD_WORDS[0]}, ещё текст',
    }
    response = author_client.post(url, data=bad_words_data)

    assertFormError(response.context['form'], 'text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, comment, form_data):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, data=form_data)
    detail_url = reverse('news:detail', args=(comment.news.id,))
    redirect_url = detail_url + '#comments'

    assertRedirects(response, redirect_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_other_user_cant_edit_comment(not_author_client, comment, form_data):
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, data=form_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_author_can_delete_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    detail_url = reverse('news:detail', args=(comment.news.id,))
    redirect_url = detail_url + '#comments'

    assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(not_author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
