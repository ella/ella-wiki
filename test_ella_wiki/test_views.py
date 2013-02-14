from django.test import TestCase
from django.contrib.auth.models import User

from ella.utils.test_helpers import create_basic_categories

from nose import tools

from .test_helpers import loader, create_wiki, create_submission

loader.register_builtin('404.html')

class ViewTestCase(TestCase):
    def setUp(self):
        super(ViewTestCase, self).setUp()
        create_basic_categories(self)
        self.superuser = User.objects.create_superuser('super', 'super@example.com', 'secret')
        self.wiki = create_wiki(self, slug='first-article')
        self.wiki2 = create_wiki(self, tree_parent=self.wiki, slug='second')


class TestWikiViews(ViewTestCase):
    def test_details_raises_404_on_no_submission(self):
        loader.register('page/content_type/ella_wiki.wiki/object.html')

        response = self.client.get('/wiki/first-article/second/')
        tools.assert_equals(404, response.status_code)

    def test_details_work_for_published_wiki(self):
        create_submission(self, wiki=self.wiki2)

        response = self.client.get('/wiki/first-article/second/')
        tools.assert_equals(200, response.status_code)

class TestCustomViews(ViewTestCase):
    def test_queue_lists_pending_submissions(self):
        sub = create_submission(self, wiki=self.wiki2)
        sub2 = create_submission(self, wiki=self.wiki2, publish=False, content='UnPublished')
        self.client.login(username='super', password='secret')

        loader.register('page/queue.html')
        response = self.client.get('/wiki/first-article/second/queue/')
        tools.assert_equals(200, response.status_code)
        tools.assert_equals([sub2], list(response.context['object_list']))

        loader.register('page/history.html')
        response = self.client.get('/wiki/first-article/second/history/')
        tools.assert_equals(200, response.status_code)
        tools.assert_equals([sub], list(response.context['object_list']))
