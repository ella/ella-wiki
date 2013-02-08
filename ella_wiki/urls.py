from django.conf.urls.defaults import patterns, url

from ella.core.urls import res

from .views import detail, queue, submission_detail, edit, history, moderation, add_child, child_queue

urlpatterns = patterns('',
    url('^%(cat)s/%(rest)s$' % res, detail, name='wiki-custom-urls'),
    url('^%(cat)s/$' % res, detail, name='wiki-detail'),
)

custom_url_patterns = patterns('',
    url('^add-child/$', add_child, name='wiki-add-child'),
    url('^child-queue/$', child_queue, name='wiki-child-queue'),

    url('^edit/$', edit, name='wiki-edit'),
    url('^queue/$', queue, name='wiki-queue'),
    url('^queue/%(id)s/$' % res, moderation, name='wiki-moderation'),

    url('^history/$', history, name='wiki-history'),
    url('^history/%(id)s/$', submission_detail, name='wiki-submission'),
)
