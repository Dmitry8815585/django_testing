from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_user_can_create_comment(author_client, author, form_data, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.post(url, data=form_data)
    reverse_url = f'{url}#comments'
    assertRedirects(response, reverse_url)
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.author_id == form_data['author_id']
    assert new_comment.text == form_data['text']
    assert new_comment.news_id == form_data['news_id']


def test_anonymous_user_cant_create_comment(client, form_data, news):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_edit_his_comment(author_client, comment, news):

    url = reverse('news:edit', kwargs={'pk': news.pk})
    response = author_client.post(url, {'text': 'updated comment'})

    url_redirect = reverse('news:detail', kwargs={'pk': news.pk})
    reverse_url = f'{url_redirect}#comments'
    assertRedirects(response, reverse_url)

    comment.refresh_from_db()
    assert comment.text == 'updated comment'


def test_user_can_delete_his_comment(author_client, comment, news):
    url = reverse('news:delete', kwargs={'pk': news.pk})
    response = author_client.post(url)

    url_redirect = reverse('news:detail', kwargs={'pk': news.pk})
    reverse_url = f'{url_redirect}#comments'
    assertRedirects(response, reverse_url)

    assert Comment.objects.filter(id=comment.id).count() == 0


def test_user_cant_delete_not_his_comment(
        form_data, reader_client, news, comment
):
    url = reverse('news:delete', kwargs={'pk': news.pk})
    response = reader_client.post(url)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_user_cant_edit_not_his_comment(
        form_data, reader_client, news, comment
):
    url = reverse('news:delete', kwargs={'pk': news.pk})
    response = reader_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND

    comment_from_db = Comment.objects.get(id=comment.id)

    assert comment.author_id == comment_from_db.author_id
    assert comment.text == comment_from_db.text
    assert comment.news_id == comment_from_db.news_id


def test_user_cant_use_bad_words(author_client, form_data, news, comment):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 1
