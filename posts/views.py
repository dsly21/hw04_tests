from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator

from .models import Post, Group, User
from .forms import PostForm


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
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
    posts = group.posts.all()[:12]

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html", {"group": group,
                                          "posts": posts,
                                          "paginator": paginator,
                                          "page": page})


@login_required
def new_post(request):

    if request.method == "POST":
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("index")
        return render(request, 'new.html', {'form': form})

    form = PostForm()
    return render(request, 'new.html', {'form': form})


def post_edit(request, username, post_id):
    edit_flag = True
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("post", username=username, post_id=post_id)
        return render("new.html", {'form': form,
                                   'edit_flag': edit_flag,
                                   'post': post})

    form = PostForm(instance=post)

    return render(request, 'new.html', {'form': form,
                                        'edit_flag': edit_flag,
                                        'post': post})


def profile(request, username):
    author_name = get_object_or_404(User, username=username)
    full_author_name = author_name.get_full_name()
    post_user = Post.objects.filter(author=author_name)
    posts_count = len(post_user)
    post = post_user.order_by('pub_date').last()

    post_list = post_user.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'profile.html', {
                            'author_name': author_name,
                            'full_author_name': full_author_name,
                            'post_user': post_user,
                            'posts_count': posts_count,
                            'page': page,
                            'paginator': paginator,
                            'post': post,
    })


def post_view(request, username, post_id):
    author_name = get_object_or_404(User, username=username)
    full_author_name = author_name.get_full_name()
    post_user = Post.objects.filter(author=author_name)
    posts_count = len(post_user)

    post = Post.objects.get(id=post_id)
    pub_date = post.pub_date

    return render(request, 'post.html', {
                                        'author_name': author_name,
                                        'full_author_name': full_author_name,
                                        'post_user': post_user,
                                        'posts_count': posts_count,
                                        'post': post,
                                        'pub_date': pub_date,
    })
