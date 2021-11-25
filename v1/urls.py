from django.urls import path, include
from . import views

app_name = 'v1'
urlpatterns = [
    path('user/signup/email-auth', views.requestEmailAuth.as_view(), name='index'),
    path('user/signup/email-auth/', views.requestEmailAuth.as_view(), name='index'),
    path('user/signup', views.signupInfoInput.as_view(), name='index'),
    path('user/signup/', views.signupInfoInput.as_view(), name='index'),
    path('user/signin', views.signinAPI.as_view(), name='index'),
    path('user/signin/', views.signinAPI.as_view(), name='index'),
    path('user', views.userAPI.as_view(), name='index'),
    path('user/', views.userAPI.as_view(), name='index'),
    path('user/data/garbage-output', views.garbage_output_api.as_view(), name='index'),
    path('user/data/garbage-output/', views.garbage_output_api.as_view(), name='index'),
    path('post/market', views.marketPostAPI.as_view(), name='index'),
    path('post/market/', views.marketPostAPI.as_view(), name='index'),
    path('post/market/connect', views.connectUser.as_view(), name='index'),
    path('post/market/connect/', views.connectUser.as_view(), name='index'),
    path('post/junk-art', views.artPostAPI.as_view(), name='index'),
    path('post/junk-art/', views.artPostAPI.as_view(), name='index'),
    path('post/junk-art/challenge', views.challengePostAPI.as_view(), name='index'),
    path('post/junk-art/challenge/', views.challengePostAPI.as_view(), name='index'),
]
