from .models import Comment
from django import forms


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',) # Comment 모델의 정보들 중 어떤 정보들을 입력받을지를 선택함
        # exclude = ('post', 'author ') /  Comment 모벨의 정보들 중 어떤 데이터들을 제외하고 입력받을지를 선택함

