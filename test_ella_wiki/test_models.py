from django.test import TestCase

from ella.utils.test_helpers import create_basic_categories

from nose import tools

from .test_helpers import create_wiki, create_submission

class TestWikiModel(TestCase):
    def setUp(self):
        super(TestWikiModel, self).setUp()
        create_basic_categories(self)

    def test_tree_path(self):
        wiki = create_wiki(self, slug='first-article')
        wiki2 = create_wiki(self, tree_parent=wiki, slug='second')

        tools.assert_equals('first-article', wiki.tree_path)
        tools.assert_equals('first-article/second', wiki2.tree_path)

        tools.assert_equals('/wiki/first-article/', wiki.get_absolute_url())
        tools.assert_equals('/wiki/first-article/second/', wiki2.get_absolute_url())

    def test_wiki_with_no_submission_is_unpublished(self):
        wiki = create_wiki(self, slug='first-article')
        tools.assert_false(wiki.is_published())

    def test_wiki_with_submission_is_published(self):
        submission = create_submission(self)
        tools.assert_true(submission.wiki.is_published())
