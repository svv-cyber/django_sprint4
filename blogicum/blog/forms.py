from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Post, Comment

User = get_user_model()


class RegistrationForm(UserCreationForm):
    """Форма регистрации пользователя."""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class ProfileEditForm(forms.ModelForm):
    """Форма редактирования профиля."""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования поста."""
    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image')
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CommentForm(forms.ModelForm):
    """Форма для комментария."""
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }