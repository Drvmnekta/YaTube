"""Module with admin panel configuration."""

from django.contrib import admin

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin panel configuration for Post model."""

    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Admin panel configuration for Group model."""
    
    list_display = ('pk', 'title')
    search_fields = ('title',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin panel configuration for Comment model."""
    
    list_display = ('post', 'author', 'text', 'created')
    search_fields = ('text',)
    list_filter = ('author', 'created', 'post')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Admin panel configuration for Follow model."""
    
    list_display = ('user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
