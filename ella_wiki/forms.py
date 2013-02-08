from django.forms.models import ModelForm
from django.template.defaultfilters import slugify

from .models import Submission, Wiki

class SubmissionForm(ModelForm):
    def __init__(self, wiki, user, *args, **kwargs):
        initial = kwargs.pop('initial', {})
        initial.content = wiki.content
        super(SubmissionForm, self).__init__(*args, initial=initial,  **kwargs)
        self.instance.wiki = wiki
        self.instance.user = user

    class Meta:
        model = Submission
        fields = ('content', 'user_comment', )

class WikiForm(ModelForm):
    def __init__(self, parent, *args, **kwargs):
        super(WikiForm, self).__init__(*args, **kwargs)
        if parent:
            self.instance.tree_parent = parent
            self.instance.category = parent.category

    def clean(self):
        if 'title' in self.cleaned_data:
            self.instance.slug = slugify(self.cleaned_data['title'])
        return super(WikiForm, self).clean()

    class Meta:
        model = Wiki
        fields = ('title', )
