from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Post, Category, Tag, Comment # '.'은 현재 폴더를 의미함
from .forms import CommentForm

class PostList(ListView):
    model = Post
    #template_name = 'blog/post_list.html'
    ordering = '-pk'

    def get_context_data(self, **kwargs): # keyword arguments
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        return context


class PostDetail(DetailView):
    model = Post

    def get_context_data(self, **kwargs): # keyword arguments
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        context['comment_form'] = CommentForm
        return context


class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView): #LoginRequiredMixin : 로그인이 되어있는 경우에만 이 페이지에 접속할 수 있게 한다. # 글 작성 페이지에 있으면 하는 것들을 Post 모델에서 선택할 것
    model = Post # template 이름을 지정하지 않을 시 post_form.html 을 기본값으로 가지게 됨
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user # request : 요청을 하는 클라이언트에 대한 정보를 담음
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser): # 로그인 한 상태면 True를 반환, 로그인하지 않은 상태면 False를 반환
            form.instance.author = current_user # form 클래스로 만들어진 인스턴스의 author 필드에 current_user(현재 로그인한 사용자)를 채워넣는다.
            response = super(PostCreate, self).form_valid(form)

            tags_str = self.request.POST.get('tags_str')
            if tags_str:
                tags_str = tags_str.strip() # 문자열 앞뒤에 빈 문자열일 있을 경우 없애줌
                tags_str = tags_str.replace(',', ';') # 문자열 사이에 ','가 있을 경우 ';'로 바꿔줌
                tags_list = tags_str.split(';') # ; 을 기준으로 문자열들을 구분해줌

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    # name이 t 인 것이 있으면 get 하고 name이 t인 것이 없으면 만든 다음에 가져오게 한다.(변수 tag)
                    # 새로 만든 경우에는 is_tag_created가 true, 기존에 있던 경우에는 false로 반환된다.
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True) # allow_unicode : 한국어로 작성해도 인식할 수 있도록 해준다.
                        # admin에서와 달리 자동으로 slug를 만들어주지 않기 때문에 모듈을 import해서 만들어주도록 한다.
                        tag.save()
                    self.object.tags.add(tag) # 새로 만든 태그가 object(이 경우에는 새로 만든 포스트)에 추가된다.
            return response

        else:
            return redirect('/blog/') # 로그인하지 않았을 경우에는 /blog/로 보낸다.


class PostUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']
    template_name = 'blog/post_update_form.html'

    def dispatch(self, request, *args, **kwargs): # args : 여러개의 인자를 튜플형태로 가져옴 / kwargs : 키워드 형태로 가져옴 / #dispatch : get 방식인지 post방식인지를 구분해준다.
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied # 다른 권한이 없으므로 200이 뜨지 않음

    def get_context_data(self, **kwargs):
        context = super(PostUpdate, self).get_context_data()
        # 기본적으로 UpdateView에서 제공하는 get_context_data를 사용하기 위해 super를 사용
        if self.object.tags.exists():
            tags_str_list = list()
            for t in self.object.tags.all():
                tags_str_list.append(t.name)
            # 존재하는 tag를 해당 포스트에 추가한다.
            context['tags_str_default'] = '; '.join(tags_str_list)
            # 존재하는 tag들(list의 요소들로 존재함)을 ; 로 구분해서 합친다. 이를 context로 저장한다.
        return context

    def form_valid(self, form):
        response = super(PostUpdate, self).form_valid(form)
        self.object.tags.clear()
        # 해당 post에 연결되어 있는 tag들과의 연결을 끊어줌(tag 자체가 사라지는 것은 아님)

        tags_str = self.request.POST.get('tags_str')
        if tags_str:
            tags_str = tags_str.strip()  # 문자열 앞뒤에 빈 문자열일 있을 경우 없애줌
            tags_str = tags_str.replace(',', ';')  # 문자열 사이에 ','가 있을 경우 ';'로 바꿔줌
            tags_list = tags_str.split(';')  # ; 을 기준으로 문자열들을 구분해줌

            for t in tags_list:
                t = t.strip()
                tag, is_tag_created = Tag.objects.get_or_create(name=t)
                # name이 t 인 것이 있으면 get 하고 name이 t인 것이 없으면 만든 다음에 가져오게 한다.(변수 tag)
                # 새로 만든 경우에는 is_tag_created가 true, 기존에 있던 경우에는 false로 반환된다.
                if is_tag_created:
                    tag.slug = slugify(t, allow_unicode=True)  # allow_unicode : 한국어로 작성해도 인식할 수 있도록 해준다.
                    # admin에서와 달리 자동으로 slug를 만들어주지 않기 때문에 모듈을 import해서 만들어주도록 한다.
                    tag.save()
                self.object.tags.add(tag)  # 새로 만든 태그가 object(이 경우에는 새로 만든 포스트)에 추가된다.

        return response


def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)
    # 이 함수의 인자로 받은 slug와 동일한 slug를 갖는 카테고리를 불러와 저장한다.

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category
        }
    )


def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'tag': tag
        }
    )

def new_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)
        # 존재하지 않는 pk 값을 가지고 있는 포스트를 요청했을 때 404 에러를 발생시킴

        if request.method == 'POST':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid(): # form이 정상적으로 작성되었을 경우 해당 내용으로 레코드를 만들어 db에 저장한다.
                comment = comment_form.save(commit=False) # db에 커밋하지 말 것
                comment.post = post
                comment.author = request.user
                comment.save()
                return redirect(comment.get_absolute_url()) # 상단의 post 필드와 author 필드를 채운 후에 저장한다.
        return redirect(post.get_absolute_url()) # get 방식으로 요청하거나 form의 형식이 올바르지 않을 경우 현 포스트 상세페이지로 리다이렉트한다.
    else:
        raise PermissionError # 권한이 없음을 나타냄


class CommentUpdate(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs): # args : 여러개의 인자를 튜플형태로 가져옴 / kwargs : 키워드 형태로 가져옴 / #dispatch : get 방식인지 post방식인지를 구분해준다.
        if request.user.is_authenticated and request.user == self.get_object().author: # 현재 접속한 유저가 게시물의 작성자일 때에만 PostUpdate 페이지로 가게 됨
            return super(CommentUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied # 다른 권한이 없으므로 200이 뜨지 않음


def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk) # 모델은 Comment를 가져오고 pk는 Comment의 pk이다.
    post = comment.post

    if request.user.is_authenticated and request.user == comment.author:
        comment.delete()
        return redirect(post.get_absolute_url())
    else:
        raise PermissionDenied # 인정받지 않은 유저이거나, 해당 댓글의 작성자가 아닌 경우

#template_name = 'blog/post_detail.html'

# Create your views here.
# def index(request):
#     posts = Post.objects.all().order_by('-pk')
#
#     return render(
#         request,
#         'blog/post_list.html', #blog 폴더의 index.html에서 해당 변수를 사용할 수 있게 함
#         {
#             'posts': posts,
#         }
#     )

# def single_post_page(request, pk):
#     post = Post.objects.get(pk=pk)
#
#     return render(
#         request,
#         'blog/post_detail.html',
#         {
#             'post':post
#         }
#     )