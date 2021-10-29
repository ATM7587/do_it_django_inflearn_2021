from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.utils.text import slugify
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Category, Tag

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
    def dispatch(self, request, *args, **kwargs): #args : 여러개의 인자를 튜플형태로 가져옴 / kwargs : 키워드 형태로 가져옴 / #dispatch : get 방식인지 post방식인지를 구분해준다.
        if request.user.is_authenticated and request.user == self.get_object().author:
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied # 다른 권한이 없으므로 200이 뜨지 않음


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