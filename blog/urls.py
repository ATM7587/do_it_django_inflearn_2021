from django.urls import path
from . import views

urlpatterns = [
    path('search/<str:q>/',views.PostSearch.as_view()),
    path('delete_comment/<int:pk>/', views.delete_comment), # comment의 pk를 사용
    path('update_comment/<int:pk>/', views.CommentUpdate.as_view()), # comment의 pk를 사용
    path('update_post/<int:pk>/', views.PostUpdate.as_view()), # post의 pk를 사용
    path('create_post/', views.PostCreate.as_view()),
    # path('<int:pk>/', views.single_post_page), # FBV
    # path('', views.index), # 아무것도 없을 시 blog 리스트를 보여주는 기능으로 이동함 #FBV
    path('tag/<str:slug>/', views.tag_page),
    path('category/<str:slug>/', views.category_page), # category_page를 함수로 만들겠다.(소문자)
    path('<int:pk>/new_comment/', views.new_comment),
    path('<int:pk>/', views.PostDetail.as_view()), # PostDetail.as_view()를 클래스로 만들겠다.(대문자)
    path('', views.PostList.as_view()),
]
