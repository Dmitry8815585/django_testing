import pytest
from django.conf import settings
from django.urls import reverse
from news.forms import CommentForm


@pytest.mark.parametrize(
    'parametrized_client, form_on_page,  expected_form_type',
    (
        (pytest.lazy_fixture('author_client'), True, CommentForm),
        (pytest.lazy_fixture('client'), False, None),
    )
)
def test_create_comment_page_contains_form(
    news, parametrized_client, form_on_page, expected_form_type
):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_on_page
    if expected_form_type:
        assert isinstance(response.context['form'], expected_form_type)
    else:
        assert 'form' not in response.context


def test_news_count(client, news_list):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_sorted_by_date):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comment_order(client, news, comment_sorted_by_date):
    url = reverse('news:detail', kwargs={'pk': news.pk})
    response = client.get(url)
    assert 'news' in response.context
    comments = response.context['news'].comment_set.all()
    all_dates = [comment.created for comment in comments]
    sorted_comments = sorted(all_dates)
    assert all_dates == sorted_comments
