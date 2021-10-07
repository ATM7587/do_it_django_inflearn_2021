from django.contrib.auth.models import User
from django.db import models
import os

class Post(models.Model):
    title = models.CharField(max_length=50)
    hook_text = models.CharField(max_length=100, blank=True)
    content = models.TextField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d', blank=True)
    # 연월일 폴더를 만들어서 그 아래에 저장하도록 함, 이미지를 등록하지 않아도 글을 저장할 수 있도록 함
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d', blank=True)

    created_at = models.DateTimeField(auto_now_add=True) # 생성일자
    updated_at = models.DateTimeField(auto_now=True)     # 수정일자

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 해당 포스트의 작성자가 삭제될 때 포스트도 같이 삭제한다.

    def __str__(self):
        return f'[{self.pk}] {self.title} :: {self.author}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]