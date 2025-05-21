from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_view, name='main'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('chat/', views.chat_view, name='chat'),
]
