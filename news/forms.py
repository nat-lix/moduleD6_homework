from django.forms import ModelForm
from .models import Post
from django import forms

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['postAuthor', 'title', 'text', 'categoryType']
        widgets = {
            'postAuthor': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя автора'
            }),
            'title': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Заголовок статьи'
            }),
            'text': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Текст Вашей статьи'
            }),
            'categoryType': forms.Select(attrs={
            'class': 'form-control',
            }),
            
       }