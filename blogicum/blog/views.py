from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from .models import Post, Category, Comment
from .forms import RegistrationForm, PostForm, CommentForm, ProfileEditForm

User = get_user_model()


def index(request):
    """Главная страница с лентой записей."""
    post_list = Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    ).order_by('-pub_date')
    
    # Пагинация: 10 постов на страницу
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, post_id):
    """Страница отдельного поста."""
    post = get_object_or_404(Post, id=post_id)
    
    # Если пользователь - автор, показываем пост даже если он не опубликован
    if request.user == post.author:
        # Показываем пост без фильтров
        pass
    else:
        # Для остальных проверяем публикацию
        if not post.is_published or not post.category.is_published or post.pub_date > timezone.now():
            raise Http404()
    
    # Получаем комментарии к посту
    comments = post.comments.all()
    
    # Форма для комментария (только для авторизованных)
    if request.user.is_authenticated:
        comment_form = CommentForm()
    else:
        comment_form = None
    
    context = {
        'post': post,
        'comments': comments,
        'form': comment_form,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Страница с постами категории."""
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')
    
    # Пагинация: 10 постов на страницу
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/category.html', {
        'category': category,
        'page_obj': page_obj
    })


def profile(request, username):
    """Страница профиля пользователя."""
    user = get_object_or_404(User, username=username)
    
    # Для автора показываем все посты, для других - только опубликованные
    if request.user == user:
        posts = Post.objects.filter(author=user).order_by('-pub_date')
    else:
        posts = Post.objects.filter(
            author=user,
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        ).order_by('-pub_date')
    
    # Пагинация: 10 постов на страницу
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile': user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


def edit_profile(request):
    """Редактирование профиля."""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'blog/edit_profile.html', {'form': form})


def edit_post(request, post_id):
    """Редактирование поста."""
    post = get_object_or_404(Post, id=post_id)
    
    # Проверяем, что автор - текущий пользователь
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)
    
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post
    )
    
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id=post.id)
    
    context = {'form': form}
    return render(request, 'blog/create.html', context)


def delete_post(request, post_id):
    """Удаление поста."""
    post = get_object_or_404(Post, id=post_id)
    
    # Проверяем, что автор - текущий пользователь
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post.id)
    
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    
    context = {'form': post}
    return render(request, 'blog/create.html', context)


def add_comment(request, post_id):
    """Добавление комментария."""
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    return redirect('blog:post_detail', post_id=post.id)


def edit_comment(request, post_id, comment_id):
    """Редактирование комментария."""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)
    
    context = {'form': form, 'comment': comment}
    return render(request, 'blog/comment.html', context)


def delete_comment(request, post_id, comment_id):
    """Удаление комментария."""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    
    # Проверяем, что автор комментария - текущий пользователь
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)
    
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)
    
    # Для GET-запроса показываем страницу подтверждения
    context = {'comment': comment}
    return render(request, 'blog/comment.html', context)


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста."""
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:profile')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


class RegistrationView(CreateView):
    """Регистрация нового пользователя."""
    form_class = RegistrationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('login')