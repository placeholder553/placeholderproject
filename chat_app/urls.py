from django.urls import path
from . import views

urlpatterns = [
    path('chat/<str:recipient_username>/', views.chat_view, name='chat'),
    path('', views.main_view,name='main'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
]