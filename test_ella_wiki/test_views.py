from django.test import TestCase

from ella.utils.test_helpers import create_basic_categories

from nose import tools

from .test_helpers import loader, create_wiki

loader.register_builtin('404.html')

class TestWikiViews(TestCase):
    def setUp(self):
        super(TestWikiViews, self).setUp()
        create_basic_categories(self)

    def test_details_raises_404_on_no_submission(self):
        wiki = create_wiki(self, slug='first-article')
        create_wiki(self, tree_parent=wiki, slug='second')

        response = self.client.get('/wiki/first-article/second/')
        tools.assert_equals(404, response.status_code)
