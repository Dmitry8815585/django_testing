from datetime import datetime, timedelta

from django.conf import settings
from django.urls import reverse

import pytest
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуру автора и клиента.
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def reader_client(reader, client):
    client.force_login(reader)
    return client


@pytest.fixture
def news(author):
    news = News.objects.create(  # Создаём объект заметки.
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        text='Текст комметария',
        author_id=author.id,
        news_id=news.id
    )
    return comment


@pytest.fixture
def news_list(author):
    news_list = [
        News(title=f'Новость {index}', text='Просто текст.')
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(news_list)
    return news_list


@pytest.fixture
def news_sorted_by_date(author):
    today = datetime.today()
    news_list = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(news_list)
    return news_list


@pytest.fixture
def comment_sorted_by_date(author, news):
    today = datetime.today()
    comment_sorted_by_date = [
        Comment(
            text='Текст комметария',
            author_id=author.id,
            news_id=news.id,
            created=today - timedelta(days=index)
        )
        for index in range(3)
    ]
    Comment.objects.bulk_create(comment_sorted_by_date)
    return comment_sorted_by_date


@pytest.fixture
def form_data(author, news):
    return {
        'text': 'Новый текст',
        'author_id': author.id,
        'news_id': news.id
    }


@pytest.fixture
def news_url(news):
    return reverse('news:detail', kwargs={'pk': news.pk})
