from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text']
        labels = {'group': 'Выберите группу', 'text': 'Введите текст'}
        help_texts = {'group': (
            'Вы можете выбрать группу, к которой будет принадлежать'
            ' ваш пост, но если вы сами по себе делать это необязательно'),
            'text': 'Здесь нужно ввести текст вашего поста'}
