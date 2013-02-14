from django.test import TestCase

from ella.utils.test_helpers import create_basic_categories

from nose import tools

from .test_helpers import create_wiki, create_submission

class TestWikiModel(TestCase):
    def setUp(self):
        super(TestWikiModel, self).setUp()
        create_basic_categories(self)
        self.wiki = create_wiki(self, slug='first-article')

    def test_tree_path(self):
        wiki2 = create_wiki(self, tree_parent=self.wiki, slug='second')

        tools.assert_equals('first-article', self.wiki.tree_path)
        tools.assert_equals('first-article/second', wiki2.tree_path)

        tools.assert_equals('/wiki/first-article/', self.wiki.get_absolute_url())
        tools.assert_equals('/wiki/first-article/second/', wiki2.get_absolute_url())

    def test_wiki_with_no_submission_is_unpublished(self):
        tools.assert_false(self.wiki.is_published())

    def test_wiki_with_submission_is_published(self):
        submission = create_submission(self, wiki=self.wiki)
        tools.assert_true(submission.wiki.is_published())


