import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUPClass(cls):
        super().setUpClass()
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()
        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.user
        )
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group-slug'
        )

    def test_create_post(self):
        """Валидная форма создает запись Post"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост2',
            'group': self.group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text']
            ).exists()
        )
        created_post = Post.objects.get(text=form_data['text'])
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.group.pk, form_data['group'])
        self.assertEqual(created_post.author, self.user)

    def test_edit_post(self):
        """Валидная форма меняет содержание записи, не дублируя ее"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Измененный тестовый пост'
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}
        ))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(
            form_data['text'],
            Post.objects.get(pk=self.post.pk).text
        )

    def test_guest_client_cant_create_post(self):
        """Неавторизованный пользователь не может создавать посты"""
        form_data = {
            'text': 'Тестовый пост2',
            'group': self.group
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        reverse_login = reverse('users:login')
        reverse_create = reverse('posts:post_create')
        self.assertRedirects(
            response, f'{reverse_login}?next={reverse_create}')

    def test_guest_client_cant_edit_post(self):
        """Неавторизованный пользователь не может редактировать посты"""
        form_data = {
            'text': 'Измененный тестовый пост'
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))

    def test_create_post_with_pic(self):
        """Валидная форма создает пост с картинкой"""
        posts_count = Post.objects.count()
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
        form_data = {
            'text': 'Тестовый пост с картинкой',
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                image='posts/small.gif'
            ).exists()
        )
        created_post = Post.objects.get(text=form_data['text'])
        self.assertEqual(created_post.text, form_data['text'])
        self.assertEqual(created_post.author, self.user)
        default_upload_path = created_post._meta.get_field('image').upload_to
        path_to_file = f"{default_upload_path}small.gif"
        self.assertEqual(
            created_post.image.name, path_to_file)

    def test_comment_create(self):
        """Валидная форма создает комментарий"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(Post.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text']
            ).exists()
        )
        created_comment = Comment.objects.get(text=form_data['text'])
        self.assertEqual(created_comment.text, form_data['text'])
        self.assertEqual(created_comment.author, self.user)

    def test_guest_client_cant_create_comment(self):
        """Неавторизованный пользователь не может создавать комментарии"""
        form_data = {
            'text': 'Тестовый комментарий от гостя',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        reverse_login = reverse('users:login')
        reverse_comment = reverse(
            'posts:add_comment', kwargs={'post_id': self.post.pk})
        self.assertRedirects(
            response, f'{reverse_login}?next={reverse_comment}')
