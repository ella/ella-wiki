from django.test import TestCase

from ella.utils.test_helpers import create_basic_categories

from ella_wiki.models import Wiki

from nose import tools

class TestWikiModel(TestCase):
    def setUp(self):
        super(TestWikiModel, self).setUp()
        create_basic_categories(self)

    def test_tree_path(self):
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
        tools.assert_equals('first-article', wiki.tree_path)
        tools.assert_equals('first-article/second', wiki2.tree_path)

        tools.assert_equals('/wiki/first-article/', wiki.get_absolute_url())
        tools.assert_equals('/wiki/first-article/second/', wiki2.get_absolute_url())
