from django.test import TestCase

from ella.utils.test_helpers import create_basic_categories

from nose import tools

from .test_helpers import loader, create_wiki, create_submission

loader.register_builtin('404.html')

class TestWikiViews(TestCase):
    def setUp(self):
        super(TestWikiViews, self).setUp()
        create_basic_categories(self)
        self.wiki = create_wiki(self, slug='first-article')
        self.wiki2 = create_wiki(self, tree_parent=self.wiki, slug='second')

    def test_details_raises_404_on_no_submission(self):
        loader.register('page/content_type/ella_wiki.wiki/object.html')
        response = self.client.get('/wiki/first-article/second/')
        tools.assert_equals(404, response.status_code)

    def test_details_work_for_published_wiki(self):
        create_submission(self, wiki=self.wiki2)

        response = self.client.get('/wiki/first-article/second/')
        tools.assert_equals(200, response.status_code)
