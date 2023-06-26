from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username='author',
            password='password'
        )
        self.reader = User.objects.create_user(
            username='reader',
            password='password'
        )
        self.note = Note.objects.create(
            title='Test Note',
            text='This is a test note.',
            author=self.author
        )
        self.note_reader = Note.objects.create(
            title='Test Note Reader',
            text='This is a test note.',
            author=self.reader
        )
        self.urls = (
            ('notes:add', None),
            ('notes:edit', [self.note.slug]),
        )
        self.client.force_login(self.author)
        self.url_list = reverse('notes:list')

    def test_anonymous_client_has_no_form(self):
        for name, args in self.urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)

    def test_note_in_object_list(self):
        response = self.client.get(self.url_list)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_list_notes_for_not_user_note(self):
        response = self.client.get(self.url_list)
        object_list = response.context['object_list']
        for note in object_list:
            self.assertNotEqual(note, self.note_reader)
