from django import forms
from .models import Topic

class NewTopicForm(forms.Form):
    title = forms.CharField(label='Title', max_length=160)
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5,
                                     'placeholder': 'Your message. The max length of the text is 1000.'}),
        label='Message',
        max_length=1000,
        #help_text='The max length of the text is 1000.',
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