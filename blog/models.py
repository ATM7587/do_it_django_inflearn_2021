from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=50)
    content = models.TextField()

    head_image = models.ImageField(upload_to='blog/images/%Y/%m/%d', blank=True)
    # 연월일 폴더를 만들어서 그 아래에 저장하도록 함, 이미지를 등록하지 않아도 글을 저장할 수 있도록 함
    created_at = models.DateTimeField(auto_now_add=True) # 생성일자
    updated_at = models.DateTimeField(auto_now=True)     # 수정일자
    # author: 추후 작성 예정

    def __str__(self):
        return f'[{self.pk}] {self.title}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'
