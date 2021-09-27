from django.shortcuts import render
from .models import Post

# Create your views here.
def index(request):
    posts = Post.objects.all().order_by('-pk')

    return render(
        request,
        'blog/index.html', #blog 폴더의 index.html에서 해당 변수를 사용할 수 있게 함
        {
            'posts': posts,
        }
    )