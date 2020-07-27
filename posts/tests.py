from django.test import TestCase, Client
from django.urls import reverse

from .models import User, Post, Group


class Test(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(
                                username="test_user",
                                email="test@test.com",
                                password="123452")

        self.new_post = Post.objects.create(
                            text='some text',
                            author=self.test_user)

        self.new_group = Group.objects.create(
                            title="test_group",
                            slug="test_slug",
                            description="test_description")

        self.anon_client = Client()
        self.client = Client()
        self.client.force_login(self.test_user)

    def get_url(self, post, group):
        urls = [reverse('index'),

                reverse('profile', kwargs={
                        'username': self.test_user.username}),

                reverse('post', kwargs={
                        'username': self.test_user.username,
                        'post_id': post.id})]
        return urls

    def test_profile(self):
        response = self.client.get('/test_user/')
        self.assertEqual(response.status_code, 200, msg='status code')

        self.assertContains(response, self.test_user,
                            msg_prefix='check create profile')

    def test_new_post_auth_user(self):
        data = {'text': 'test_text', 'group': self.new_group.id}

        response = self.client.post(reverse('new_post'), data)
        self.assertEqual(response.status_code, 302, msg='redirect check')

        response = self.client.get('')
        self.assertContains(response, 'test_text', status_code=200,
                            msg_prefix='check new post in index page')

    def test_new_post_not_auth(self):
        data = {'text': 'test_text', 'group': self.new_group.id}
        response = self.anon_client.post(reverse('new_post'), data)

        login_url = reverse('login')
        new_post_url = reverse('new_post')
        url = f'{login_url}?next={new_post_url}'

        self.assertRedirects(response, url, status_code=302,
                             target_status_code=200,
                             msg_prefix='redirect user, if he is\'t auth')

    def test_post_view(self):
        for url in self.get_url(post=self.new_post, group=self.new_group):
            response = self.client.get(url)

            self.assertContains(response, self.new_post.text,
                                msg_prefix='check new post in all pages')

    def test_post_edit_auth_user(self):
        post = Post.objects.create(
                                   text='test text',
                                   group=self.new_group,
                                   author=self.test_user)

        group = Group.objects.create(
                                     title='changed_group',
                                     slug='changed_group',
                                     description='changed_description')

        data = {'text': 'edit text', 'group': group.id}

        response = self.client.post(reverse('post_edit', kwargs={
                                'username': post.author.username,
                                'post_id': post.id}),
                                 data, follow=True)

        post.refresh_from_db()

        urls = self.get_url(post=post, group=group)
        for url in urls:
            self.assertContains(response, post.text,
                                msg_prefix='post text changed')

            self.assertContains(response, post.author,
                                msg_prefix='post author changed')

        response = self.client.get(reverse('group_posts',
                                   kwargs={'slug': group.slug}))

        self.assertContains(response, post.group,
                            msg_prefix='post group changed')
