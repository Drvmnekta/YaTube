from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
# from django.core.cache import cache
from django.views.decorators.cache import cache_page

from yatube.settings import PAGINATION_NUM

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def pagination(request, post_list, num_on_page):
    paginator = Paginator(post_list, num_on_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(60 * 15)
def index(request):
    template = 'posts/index.html'
#   post_list = cache.get('index_page')
#    if post_list is None:
#        post_list = Post.objects.all()
#        cache.set('index_page', post_list, timeout=20)
    post_list = Post.objects.all()
    page_obj = pagination(request, post_list, PAGINATION_NUM)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = pagination(request, post_list, PAGINATION_NUM)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        if Follow.objects.filter(author=author, user=request.user).exists():
            following = True
    post_list = author.posts.all()
    posts_num = author.posts.count()
    page_obj = pagination(request, post_list, PAGINATION_NUM)
    context = {
        'author': author,
        'page_obj': page_obj,
        'posts_num': posts_num,
        'following': following,
    }
    return render(request, template, context)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = pagination(request, post_list, PAGINATION_NUM)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    following = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=following
    ).delete()
    return redirect('posts:profile', username=username)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    posts_num = post.author.posts.count()
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'posts_num': posts_num,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    groups = Group.objects.all()
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    context = {
        'form': form,
        'groups': groups
    }
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context)
    instance = form.save(commit=False)
    instance.author = request.user
    instance.save()
    return redirect('posts:profile', username=request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    context = {
        'is_edit': True,
        'form': form,
        'post': post
    }
    if not form.is_valid():
        return render(request, 'posts/create_post.html', context)
    form.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, pk=post_id)
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
