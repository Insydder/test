from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

from .models import Post, Group
from .forms import PostForm

NUM_OF_POSTS = 10
User = get_user_model()


def paginate(request, posts):
    paginator = Paginator(posts, NUM_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    post_list = Post.objects.all()
    page_obj = paginate(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    posts = group.posts.all()
    page_obj = paginate(request, posts)
    desc = group.description
    context = {
        'group': group,
        'page_obj': page_obj,
        'desc': desc,
    }
    return render(request, 'posts/group_list.html', context)


def group_list(request):
    template = 'posts/group_list.html'
    return render(request, template)


def profile(request, username):
    username = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=username)
    total_num_posts = user_posts.count()
    page_obj = paginate(request, user_posts)
    context = {
        'username': username,
        'user_posts': user_posts,
        'total_num_posts': total_num_posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    posts = post.author.posts.count()
    context = {
        'post': post,
        'posts': posts,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', context={'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    is_edit = True
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post)
    if post.author != request.user:
        return redirect('posts:post_detail')
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(
        request,
        "posts/create_post.html",
        context={"form": form, "is_edit": is_edit, "post": post},
    )
