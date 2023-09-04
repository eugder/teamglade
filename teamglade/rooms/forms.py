from django import forms

class NewTopicForm(forms.Form):
    title = forms.CharField(label='Title', max_length=100)
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'What is on your mind?'}),
        label='Message',
        max_length=4000,
        help_text='The max length of the text is 4000.',
    )
