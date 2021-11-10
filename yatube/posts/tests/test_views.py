import datetime as dt
import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post
from yatube.settings import PAGINATION_NUM

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.user_no_posts = User.objects.create_user(
            username='TestUserNoPosts')
        cls.authorized_client_no_posts = Client()
        cls.authorized_client_no_posts.force_login(cls.user_no_posts)
        cls.user_not_follow = User.objects.create_user(
            username='TestUserNotFollow')
        cls.authorized_client_not_follow = Client()
        cls.authorized_client_not_follow.force_login(cls.user_not_follow)
        cls.group_no_posts = Group.objects.create(
            title='Тестовая группа без постов',
            slug='group-no-posts'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug'
        )
        Post.objects.bulk_create([
            Post(
                text=f'Тестовый пост {x}',
                author=cls.user,
                group=cls.group,
            )
            for x in range(12)
        ])
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post_with_pic = Post.objects.create(
            text='Пост с картинкой',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )
        cls.posts = Post.objects.all()[:13]

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def check_context(self, response, user, group, num):
        for i in range(num):
            for j in range(num - 1, 0):
                cur_obj = response.context['page_obj'][i]
                self.assertEqual(cur_obj.text, f'Тестовый пост {j}')
                self.assertEqual(cur_obj.author, user)
                self.assertEqual(cur_obj.group, group)
                self.assertEqual(cur_obj.pub_date, dt.date.today())

    def test_pages_uses_correct_templates(self):
        """Адреса используют соответствующие шаблоны"""
        templates_pages = {
            'posts/index.html': reverse('posts:index'),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': self.user.username}),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': self.posts[1].pk}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_index_first_page_contains_ten_records(self):
        """Первая страница паджинатора на главной странице"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self. assertEqual(len(response.context['page_obj']), PAGINATION_NUM)

    def test_index_second_page_contains_three_records(self):
        """Вторая страница паджинатора на главной странице"""
        response = self.authorized_client.get(reverse(
            'posts:index') + '?page=2')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self. assertEqual(len(response.context['page_obj']), 3)

    def test_group_paginator_first_page(self):
        """Первая страница паджинатора на странице группы"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.context['page_obj']), PAGINATION_NUM)

    def test_group_paginator_second_page(self):
        """Вторая страница паджинатора на странице группы"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}) + '?page=2')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self. assertEqual(len(response.context['page_obj']), 3)

    def test_profile_paginator_first_page(self):
        """Первая страница паджинатора на странице пользователя"""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self. assertEqual(len(response.context['page_obj']), PAGINATION_NUM)

    def test_profile_paginator_second_page(self):
        """Вторая страница паджинатора на странице пользователя"""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}) + '?page=2')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self. assertEqual(len(response.context['page_obj']), 3)

    def test_index_show_correct_context(self):
        """Корректные посты на главной странице"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.check_context(response, self.user, self.group, 13)

    def test_group_show_correct_context(self):
        """Корректные посты на странице группы"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.check_context(response, self.user, self.group, 13)

    def test_profile_show_correct_context(self):
        """Корректные посты на странице пользователя"""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.check_context(response, self.user, self.group, 13)

    def test_group_page_show_correct_group(self):
        """Корректная группа передается в шаблон"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        cur_group = response.context['group']
        self.assertEqual(self.group, cur_group)

    def test_profile_page_show_correct_user(self):
        """Корректный пользователь передается в шаблон"""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        cur_user = response.context['author']
        self.assertEqual(self.user, cur_user)

    def test_create_form_is_correct(self):
        """Поля формы на странице создания поста корректного типа"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_form_is_correct(self):
        """Поля формы на странице редактирования поста корректного типа"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.posts[0].pk}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_form_suggests_correct_groups(self):
        """При создании поста форма предлагает корректные группы"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        cur_groups = list(response.context['groups'])
        self.assertEqual(cur_groups, list(Group.objects.all()))

    def test_edit_form_suggests_correct_post(self):
        """Форма для редактирования поста дает редактировать корректный пост"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.posts[0].pk}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        cur_post = response.context['post']
        self.assertEqual(cur_post, self.posts[0])

    def test_post_detail_shows_correct_post(self):
        """Страница поста, показывает корректный пост"""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.posts[0].pk}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        cur_post = response.context['post']
        self.assertEqual(cur_post, self.posts[0])

    def test_new_post_not_in_incorrect_group(self):
        """Созданный пост не появляется в несвоей группе"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group_no_posts.slug}
        ))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn(self.posts[0], response.context.get('page_obj'))

    def test_image_in_index_context(self):
        """При выводе поста с картинкой
        изображение передается в контексте на главную страницу."""
        response = self.authorized_client.get(reverse('posts:index'))
        last_post = response.context['page_obj'][0]
        self.assertIsNotNone(last_post.image)
        default_upload_path = last_post._meta.get_field('image').upload_to
        path_to_file = f"{default_upload_path}small.gif"
        self.assertEqual(
            last_post.image.name, path_to_file)

    def test_image_in_group_context(self):
        """При выводе поста с картинкой
        изображение передается в контексте на страницу группы."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        last_post = response.context['page_obj'][0]
        self.assertIsNotNone(last_post.image)
        default_upload_path = last_post._meta.get_field('image').upload_to
        path_to_file = f"{default_upload_path}small.gif"
        self.assertEqual(
            last_post.image.name, path_to_file)

    def test_image_in_profile_context(self):
        """При выводе поста с картинкой
        изображение передается в контексте на страницу профайла."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        last_post = response.context['page_obj'][0]
        self.assertIsNotNone(last_post.image)
        default_upload_path = last_post._meta.get_field('image').upload_to
        path_to_file = f"{default_upload_path}small.gif"
        self.assertEqual(
            last_post.image.name, path_to_file)

    def test_cache_index(self):
        """Главная страница кешируется"""
        response_first = self.authorized_client.get(reverse('posts:index'))
        post_to_delete = Post.objects.get(text='Пост с картинкой')
        post_to_delete.delete()
        response_after_del = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_first.content, response_after_del.content)
        cache.clear()
        response_after_clear = self.authorized_client.get(
            reverse('posts:index'))
        self.assertNotEqual(
            response_after_del.content, response_after_clear.content)

    def test_user_can_follow(self):
        """Авторизованный пользователь может подписываться на других"""
        follow_count = Follow.objects.filter(user=self.user_no_posts).count()
        self.authorized_client_no_posts.get(reverse(
            'posts:profile_follow', kwargs={'username': self.user.username}))
        self.assertTrue(
            Follow.objects.filter(
                author=self.user,
                user=self.user_no_posts
            ).exists()
        )
        self.assertEqual(
            Follow.objects.filter(user=self.user_no_posts).count(), follow_count + 1)

    def test_user_can_unfollow(self):
        """Авторизованный пользователь может удалять из подписок"""
        self.authorized_client_no_posts.get(reverse(
            'posts:profile_unfollow', kwargs={'username': self.user.username}))
        self.assertFalse(
            Follow.objects.filter(
                author=self.user,
                user=self.user_no_posts
            ).exists()
        )

    def test_new_post_appears_at_followers(self):
        """Новая запись появляется в ленте подписчиков"""
        Follow.objects.create(
            author=self.user,
            user=self.user_no_posts
        )
        new_post = Post.objects.create(
            text='Тестовый пост для подписчиков1',
            author=self.user
        )
        response = self.authorized_client_no_posts.get(reverse(
            'posts:follow_index'
        ))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(new_post, response.context['page_obj'])

    def test_new_post_doesnt_appear_at_non_followers(self):
        """Новая запись не в ленте не подписчиков"""
        new_post = Post.objects.create(
            text='Тестовый пост для подписчиков2',
            author=self.user
        )
        response = self.authorized_client_not_follow.get(reverse(
            'posts:follow_index'
        ))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn(new_post, response.context['page_obj'])
