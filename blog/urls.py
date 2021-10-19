from django.urls import path
from . import views


urlpatterns = [
    # path('<int:pk>/', views.single_post_page), # FBV
    # path('', views.index), # 아무것도 없을 시 blog 리스트를 보여주는 기능으로 이동함 #FBV
    path('category/<str:slug>/', views.category_page), # category_page를 함수로 만들겠다.(소문자)
    path('<int:pk>/', views.PostDetail.as_view()), # PostDetail.as_view()를 클래스로 만들겠다.(대문자)
    path('', views.PostList.as_view()),
]
