from django.urls import path
from . import views

urlpatterns = [
    path('', views.members, name='members'),
    path('test/', views.test, name='test'),
]