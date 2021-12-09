from django.urls import path
from . import views


urlpatterns = [
    path('<int:movie_pk>/', views.movie_detail),
    path('<int:movie_pk>/like/', views.movie_like),  # 영화 좋아요
    path('<int:movie_pk>/like/only/', views.movie_like_only),  # 영화 무조건 좋아요만

    path('review/', views.review_list),
    path('<int:movie_pk>/review/', views.review_create),
    path('<int:movie_pk>/review/user/<int:user_pk>/', views.user_review),  # 해당 영화에 해당 유저가 작성한 리뷰 반환
    path('review/<int:review_pk>/', views.review_detail),
    path('review/<int:review_pk>/like/', views.review_like),  # 리뷰 좋아요

    path('review/<int:review_pk>/comment/', views.review_comment_list_create),
    path('review/comment/<int:comment_pk>/', views.review_comment_detail),

    path('collection/', views.collection_list_create),
    path('collection/<int:collection_pk>/', views.collection_detail),
    path('collection/<int:collection_pk>/like', views.collection_like), # 컬렉션 라이크 

    path('collection/<int:collection_pk>/comment/', views.collection_comment_list_create),
    path('collection/comment/<int:comment_pk>/', views.collection_comment_detail),
    path('collection/comment/<int:comment_pk>/like/', views.collection_comment_like),

    # path('search/', views.search),
    # path('<int:movie_pk>/bookmark/', views.bookmark_create),  # 해당 영화에 해당 유저가 작성한 북마크 반환 & 북마크 생성
]