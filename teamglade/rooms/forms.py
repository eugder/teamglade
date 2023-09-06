from django import forms

class NewTopicForm(forms.Form):
    title = forms.CharField(label='Title', max_length=160)
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'What is on your mind?'}),
        label='Message',
        max_length=1000,
        help_text='The max length of the text is 1000.',
    )
