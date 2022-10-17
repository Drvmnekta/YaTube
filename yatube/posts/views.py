"""Module with views of posts app."""

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, Page
from django.db.models.query import QuerySet
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
# from django.core.cache import cache
from django.views.decorators.cache import cache_page

from yatube.settings import PAGINATION_NUM

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def pagination(
    request: HttpRequest, post_list: QuerySet, num_on_page: int,
    ) -> Page:
    """Get paginated page.
    
    Args:
        request: the current request;
        post_list: post objects to paginate;
        num_on_page: amount of objects on page.
    
    Returns:
        paginated page.
    """
    paginator = Paginator(post_list, num_on_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(60 * 15)
def index(request: HttpRequest) -> HttpResponse:
    """View-function of main page."""
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


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    """View-function of page with posts of exact group.
    
    Args:
        request: HttpRequest from user;
        slug: slug of the group to view posts of.
    
    Returns:
        HttpResponse of group posts page.
    """
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = pagination(request, post_list, PAGINATION_NUM)
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, template, context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """View of profile pgae.
    
    Args:
        request: HttpRequest from user;
        username: username of the profile to view.

    Returns:
        HttpResponse of profile page.
    """
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
def follow_index(request: HttpRequest) -> HttpResponse:
    """View of the page with all subscriptions."""
    template = 'posts/follow.html'
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = pagination(request, post_list, PAGINATION_NUM)
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


@login_required
def profile_follow(
    request: HttpRequest, username: str,
    ) -> HttpResponseRedirect:
    """View to follow user.
    
    Args:
        request: HttpRequest from user;
        username: username of the profile to follow.
    
    Returns:
        redirect to profile page of followed user.
    """
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(
    request: HttpRequest, username: str,
    ) -> HttpResponseRedirect:
    """View to unfollow user.
    
    Args:
        request: HttpRequest from user;
        username: username of the profile to unfollow.
    
    Returns:
        redirect to profile page of unfollowed user.
    """
    following = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author=following
    ).delete()
    return redirect('posts:profile', username=username)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """View of the page with post details."""
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
def post_create(request: HttpRequest) -> HttpResponseRedirect:
    """View of post creation."""
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
def post_edit(request: HttpRequest, post_id: int) -> HttpResponseRedirect:
    """View of post updation."""
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
def add_comment(request: HttpRequest, post_id: int) -> HttpResponseRedirect:
    """View of comment creation."""
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, pk=post_id)
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
