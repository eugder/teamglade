from django import forms
from .models import Topic

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class NewTopicForm(forms.Form):
    title = forms.CharField(label='Title', max_length=100)
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5,
                                     'placeholder': 'Your message. The max length of the text is 1000.'}),
        label='Message',
        max_length=1000,
        #help_text='The max length of the text is 1000.',
    )
    files = MultipleFileField(
        label='Select a file',
        help_text='max. 42 megabytes',
        widget=MultipleFileInput(attrs={"multiple": True}), required=False
    )

class NewTopicModelForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Your message'}),
        label='Message',
        max_length=1000,
        help_text='The max length of the text is 1000.',
    )

    class Meta:
        model = Topic
        fields = ['title', 'message']


class SendInviteForm(forms.Form):
    email = forms.EmailField(initial="test@test.com")