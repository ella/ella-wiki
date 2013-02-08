from django.test import TestCase

from ella.utils.test_helpers import create_basic_categories

from ella_wiki.models import Wiki

from nose import tools

from .test_helpers import loader

loader.register_builtin('404.html')

class TestWikiViews(TestCase):
    def setUp(self):
        super(TestWikiViews, self).setUp()
        create_basic_categories(self)

    def test_details_raises_404_on_no_submission(self):
        wiki = Wiki(
            slug='first-article',
            category=self.category,
        )
        wiki.save()
        wiki2 = Wiki(
            tree_parent=wiki,
            slug='second',
            category=self.category
        )
        wiki2.save()

        response = self.client.get('/wiki/first-article/second/')
        tools.assert_equals(404, response.status_code)
