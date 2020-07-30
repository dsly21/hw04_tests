from django.test import TestCase, Client
from django.urls import reverse

from .models import User, Post, Group


class Test(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(
                                username="test_user",
                                email="test@test.com",)

        self.new_group = Group.objects.create(
                            title="test_group",
                            slug="test_slug",
                            description="test_description")

        self.anon_client = Client()
        self.client = Client()
        self.client.force_login(self.test_user)

    def get_url(self, post, group, user):
        urls = [reverse('index'),

                reverse('profile', kwargs={
                        'username': user.username}),

                reverse('post', kwargs={
                        'username': self.test_user.username,
                        'post_id': post.id}),

                reverse('group_posts',
                        kwargs={'slug': group.slug})]

        return urls

    def requests_and_checks(self, url, group, user, text):
        response = self.client.get(url)
        if 'paginator' in response.context:
            current_post = response.context['paginator'].object_list.first()
        else:
            current_post = response.context['post']
        self.assertEqual(current_post.text, text, msg='check text failed')
        self.assertEqual(current_post.group, group, msg='check group failed')
        self.assertEqual(current_post.author, user, msg='check autor failed')

    def test_profile(self):
        response = self.client.get(reverse('profile', kwargs={
                        'username': self.test_user.username}))

        self.assertEqual(response.status_code, 200, msg='status code failed')

        self.assertContains(response, self.test_user,
                            msg_prefix='check profile failed')

    def test_new_post_auth_user(self):
        data = {'text': 'test_text', 'group': self.new_group.id}

        response = self.client.post(reverse('new_post'), data, follow=True)
        self.assertEqual(response.status_code, 200, msg='redirect check')

        post = Post.objects.all()
        self.assertEqual(len(post), 1, msg='count posts > 1')
        post = Post.objects.first()

        urls = self.get_url(post=post, group=post.group, user=post.author)
        for url in urls:
            self.requests_and_checks(
                                    url=url,
                                    group=post.group,
                                    user=post.author,
                                    text=post.text)

    def test_new_post_not_auth(self):
        data = {'text': 'test_text', 'group': self.new_group.id}
        response = self.anon_client.post(reverse('new_post'), data)

        login_url = reverse('login')
        new_post_url = reverse('new_post')
        url = f'{login_url}?next={new_post_url}'

        self.assertRedirects(response, url, status_code=302,
                             target_status_code=200,
                             msg_prefix='redirect user failed')

        post = Post.objects.all()
        self.assertEqual(len(post), 0, msg='post created')

    def test_post_view_in_all_pages(self):
        post = Post.objects.create(
                            text='some text',
                            author=self.test_user,
                            group=self.new_group,)

        urls = self.get_url(post=post, group=post.group, user=post.author)
        for url in urls:
            self.requests_and_checks(
                                    url=url,
                                    group=post.group,
                                    user=post.author,
                                    text=post.text)

    def test_post_edit_auth_user(self):
        post = Post.objects.create(
                                   text='test text',
                                   group=self.new_group,
                                   author=self.test_user)

        group = Group.objects.create(
                                     title='changed_group',
                                     slug='changed_group',
                                     description='changed_description')

        data = {'text': 'changed_text', 'group': group.id}

        self.client.post(
                        reverse('post_edit', kwargs={
                                'username': post.author.username,
                                'post_id': post.id}), data, follow=True)

        post = Post.objects.get(id=post.id)

        urls = self.get_url(post=post, group=post.group, user=post.author)
        for url in urls:
            self.requests_and_checks(
                                    url=url,
                                    group=post.group,
                                    user=post.author,
                                    text=post.text)

        response = self.client.get(reverse('group_posts', kwargs={
                                            'slug': self.new_group.slug}))

        self.assertNotEqual(response.context['group'],
                            post.group,
                            msg='check change group faled')
