"""Module with forms."""

from django import forms

from yatube.posts.models import Comment, Post


class PostForm(forms.ModelForm):
    """Class of Post form."""

    class Meta:
        """Meta-class for PostForm class."""

        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа поста',
            'image': 'Картинка к посту'
        }


class CommentForm(forms.ModelForm):
    """Class of Comment form."""

    class Meta:
        """Meta-class for CommentForm class."""

        model = Comment
        fields = {'text'}
        labels = {
            'text': 'Текст комментария'
        }
