from django.contrib.auth.models import User
from django.db import models
import os

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    # 텍스트로 고유 URL을 만들 때 주로 사용함 / allow_unicode로 한글로도 작성할 수 있게 함

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/' # slug : 모든 문자를 소문자화하고, 공백은 -로 교체

    class Meta:
        verbose_name_plural = 'Categories'
    # 복수형이 어떻게 표시될지를 직접 지정함

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    # 텍스트로 고유 URL을 만들 때 주로 사용함 / allow_unicode로 한글로도 작성할 수 있게 함

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/' # slug : 모든 문자를 소문자화하고, 공백은 -로 교체


class Post(models.Model):
    title = models.CharField(max_length=50)
    hook_text = models.CharField(max_length=100, blank=True)
    content = models.TextField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d', blank=True)
    # 연월일 폴더를 만들어서 그 아래에 저장하도록 함, 이미지를 등록하지 않아도 글을 저장할 수 있도록 함
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d', blank=True)

    created_at = models.DateTimeField(auto_now_add=True) # 생성일자
    updated_at = models.DateTimeField(auto_now=True)     # 수정일자

    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    # 해당 포스트의 작성자가 삭제될 때 포스트도 같이 삭제한다.

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, blank=True) # 카테고리는 여러개 지정하고, 없앨 수 있기 때문에, on_delete는 사옹하지 않는다.

    def __str__(self):
        return f'[{self.pk}] {self.title} :: {self.author}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]