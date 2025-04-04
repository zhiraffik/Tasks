from django.urls import path
from . import views
urlpatterns=[
    path('',views.index,name="index"),
    path('create/',views.createCard,name="create"),
    path('articles/<int:pk>/', views.article_detail, name='article_detail')
]