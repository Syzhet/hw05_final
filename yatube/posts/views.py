from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required


from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


LIMIT_OF_POSTS = 10


def index(request):
    post_list = Post.objects.all()
    context = dict(page_obj=pagination(request, post_list))
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = dict(
        group=group,
        page_obj=pagination(request, post_list)
    )
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user, author=author)
    following = False
    context = dict(
        author=author,
        page_obj=pagination(request, post_list),
        following=following
    )
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm()
    context = dict(
        post=post,
        comments=comments,
        form=form,
    )
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    instance = form.save(commit=False)
    instance.author = request.user
    instance.save()
    return redirect('posts:profile', request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    if not form.is_valid():
        return render(
            request,
            'posts/create_post.html',
            {'form': form, 'is_edit': True, 'post': post}
        )
    form.save()
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    follow_list_obj = Follow.objects.filter(user=request.user)
    follow_list_values = follow_list_obj.values_list("author", flat=True)
    post_list = Post.objects.filter(author__in=follow_list_values)
    context = dict(page_obj=pagination(request, post_list))
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
        return redirect('posts:profile', author.username)
    return redirect('posts:profile', author.username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:profile', author.username)


def pagination(request, post_list):
    paginator = Paginator(post_list, LIMIT_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
