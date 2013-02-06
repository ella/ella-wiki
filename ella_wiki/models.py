from redis import Redis

from django.db import models
from django.contrib.auth.models import User

from ella.core.models import Publishable
from ella.core.cache.utils import get_cached_object
from ella.core.cache.fields import CachedForeignKey
from ella.core.custom_urls import resolver
from ella.utils.timezone import now

from .conf import wiki_settings

redis = Redis(**wiki_settings.REDIS)

REDIS_KEY = 'wiki:%s'

class Submission(models.Model):
    STATUS_PENDING = 'P'
    STATUS_APPROVED = 'A'
    STATUS_REJECTED = 'R'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    )

    STATUS_MODERATION_CHOICES = (
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    )

    wiki = CachedForeignKey('Wiki')
    submit_date = models.DateTimeField(default=now)
    user = CachedForeignKey(User, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=1, db_index=True,
                              choices=STATUS_CHOICES, default=STATUS_PENDING)
    moderation_user = CachedForeignKey(User, null=True, on_delete=models.SET_NULL,
                                           related_name='moderated_submissions')
    moderation_date = models.DateTimeField(null=True)
    content = models.TextField()
    user_comment = models.TextField(default='')

    def get_absolute_url(self):
        return resolver.reverse(self.wiki, 'comments-list', id=self.pk)

    def set_live(self):
        self.wiki.submission = self
        self.wiki.content = self.content
        self.wiki.save(force_update=True)

    def get_by_tree_path(self, tree_path):
        pk = redis.get(REDIS_KEY % tree_path)
        if pk:
            return get_cached_object(Wiki, pk=pk)
        raise Wiki.DoesNotExist()


class Wiki(Publishable):
    tree_parent = CachedForeignKey(Publishable, related_name='children')

    content = models.TextField()

    tree_path = models.CharField(max_length=255, unique=True, editable=False)

    @models.permalink
    def get_absolute_url(self):
        return 'wiki-detail', (), {'category': self.tree_path}

    def delete(self):
        pipe = redis.pipeline()
        pipe.delete(REDIS_KEY % self.tree_path)
        super(Wiki, self).delete()
        pipe.execute()

    def save(self, **kwargs):
        "Override save() to construct tree_path based on the wiki's parent."
        old_tree_path = self.tree_path
        pipe = redis.pipeline()
        if self.tree_parent:
            self.tree_path = '%s/%s' % (self.tree_parent.tree_path, self.slug)
        else:
            self.tree_path = self.slug
        pipe.delete(REDIS_KEY % old_tree_path)
        super(Wiki, self).save(**kwargs)
        pipe.set(REDIS_KEY % old_tree_path, self.pk)
        pipe.execute()
        if old_tree_path != self.tree_path:
            # the tree_path has changed, update children
            children = Wiki.objects.filter(tree_parent=self)
            for child in children:
                child.save(force_update=True)
