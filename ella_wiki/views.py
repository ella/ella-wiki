from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.http import Http404, HttpResponse
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.core.paginator import Paginator, InvalidPage

from ella.core.cache.utils import get_cached_object
from ella.core import custom_urls
from ella.api import render_as_api
from ella.core.signals import object_rendering, object_rendered
from ella.core.views import get_templates_from_publishable


from .conf import wiki_settings
from .models import redis, Wiki, REDIS_KEY, Submission
from .forms import WikiForm, SubmissionForm

mod_required = user_passes_test(wiki_settings.IS_MODERATOR_FUNC)

def detail(request, category, url_remainder=''):
    path = category.split('/')

    # construct all possible tree_paths and get their IDs from redis
    part = []
    pipe = redis.pipeline()
    for p in path:
        part.append(p)
        pipe.get(REDIS_KEY % '/'.join(part))
    ids = pipe.execute()

    # no IDs -> 404
    if not any(ids):
        raise Http404()
    # get the last ID == the most specific wiki object
    id = filter(None, ids)[-1]
    wiki = get_cached_object(Wiki, pk=id)

    if not (wiki.is_published() or wiki_settings.IS_MODERATOR_FUNC(request.user)):
        # future publish, render if accessed by moderator
        raise Http404()

    # treat the rest as part of custom_urls part
    leftover = category[len(wiki.tree_path):]

    object_rendering.send(sender=Wiki, request=request, category=wiki.category, publishable=wiki)
    context = {
        'category': wiki.category,
        'object': wiki,
        'content_type': wiki.content_type,
    }

    # custom urls
    if leftover or url_remainder:
        url_remainder = ('%s/%s' % (leftover, url_remainder)). strip('/') + '/'
        return custom_urls.resolver.call_custom_view(request, wiki, url_remainder, context)

    # ella API
    response = render_as_api(request, wiki)
    if response:
        return response

    # custom detail
    if custom_urls.resolver.has_custom_detail(wiki):
        return custom_urls.resolver.call_custom_detail(request, context)

    object_rendered.send(sender=Wiki, request=request, category=wiki.category, publishable=wiki)

    return TemplateResponse(request, get_templates_from_publishable('object.html', wiki), context)

# django generic views suck
def get_paginated_view(attr_name, template_name, paginate_by=20):
    def paginated_view(request, context):
        qset = getattr(context['object'], attr_name)()

        paginator = Paginator(qset, paginate_by)
        try:
            page = paginator.page(request.GET.get('p', 1))
        except InvalidPage:
            raise Http404()
        context.update({
                'page': page,
                'object_list': page.object_list,
            })
        return TemplateResponse(
                request,
                get_templates_from_publishable(template_name, context['object']),
                context
            )
    return paginated_view

child_queue = mod_required(get_paginated_view('child_queue', 'child_queue.html'))
queue = mod_required(get_paginated_view('queue', 'queue.html'))
history = get_paginated_view('history', 'history.html')

@login_required
def edit(request, context):
    data = None
    if request.method == 'POST':
        data = request.POST
    form = SubmissionForm(context['object'], request.user, data)
    if form.is_valid():
        submission = form.save()
        # pre-approve moderator submissions
        if wiki_settings.IS_MODERATOR_FUNC(request.user):
            submission.approve(request.user)
        return redirect(context['object'])

    context['form'] = form
    return TemplateResponse(
            request,
            get_templates_from_publishable('submission_form.html', context['object']),
            context
        )

@login_required
def add_child(request, context):
    data = None
    if request.method == 'POST':
        data = request.POST

    wiki = None
    wform = WikiForm(context['object'], data)
    if wform.is_valid():
        wiki = wform.save(commit=False)

    sform = SubmissionForm(wiki, request.user, data)
    if sform.is_valid() and wform.is_valid():
        wiki.save()
        submission = sform.save()
        # pre-approve moderator submissions
        if wiki_settings.IS_MODERATOR_FUNC(request.user):
            submission.approve(request.user)
            return redirect(wiki)
        return redirect(context['object'])

    context['wiki_form'] = wform
    context['submission_form'] = sform
    return TemplateResponse(
            request,
            get_templates_from_publishable('child_form.html', context['object']),
            context
        )

@require_POST
@mod_required
def moderation(request, context, submission_id):
    try:
        submission = context['object'].queue.get(pk=submission_id)
    except Submission.DoesNotExist:
        raise Http404()

    submission.moderation_user = request.user
    if request.POST.get('approve', False):
        submission.approve(request.user)
    else:
        submission.reject(request.user)

    if request.is_ajax():
        return HttpResponse('{"error": false}', content_type="application/javascript")

    return redirect(submission)

def submission_detail(request, context, submission_id):
    try:
        submission = context['object'].history.get(pk=submission_id)
    except Submission.DoesNotExist:
        raise Http404()

    context['submission'] = submission
    return TemplateResponse(
            request,
            get_templates_from_publishable('submission.html', context['object']),
            context
        )
