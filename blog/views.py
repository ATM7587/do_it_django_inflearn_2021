from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
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


class PostCreate(CreateView): # 글 작성 페이지에 있으면 하는 것들을 Post 모델에서 선택할 것
    model = Post # template 이름을 지정하지 않을 시 post_form.html 을 기본값으로 가지게 됨
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']


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