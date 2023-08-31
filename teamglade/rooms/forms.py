from django import forms

class NewTopicForm(forms.Form):
    title = forms.CharField(lable='Title', max_length=100)
    message = forms.CharField(label='Message', max_length=4000)