from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/', views.single_post_page),
    path('', views.index), # 아무것도 없을 시 blog 리스트를 보여주는 기능으로 이동함
]