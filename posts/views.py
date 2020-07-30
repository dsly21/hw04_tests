from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator

from .models import Post, Group, User
from .forms import PostForm


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group,
                                          "posts": posts,
                                          "paginator": paginator,
                                          "page": page})


@login_required
def new_post(request):

    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("index")
    return render(request, 'new.html', {'form': form})


@login_required
def post_edit(request, username, post_id):
    edit_flag = True
    post = get_object_or_404(Post, id=post_id)

    form = PostForm(request.POST or None, instance=post)

    if form.is_valid():
        form.save()
        return redirect("post", username=username, post_id=post_id)

    return render(request, 'new.html', {'form': form,
                                        'edit_flag': edit_flag,
                                        'post': post})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_user = author.posts.all()
    posts_count = post_user.count()

    paginator = Paginator(post_user, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'profile.html', {
                            'author': author,
                            'posts_count': posts_count,
                            'page': page,
                            'paginator': paginator,
    })


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    post_list = post.author.posts.all()
    posts_count = post_list.count()

    return render(request, 'post.html', {
                                        'posts_count': posts_count,
                                        'post': post,
                                        'author': author,
    })
