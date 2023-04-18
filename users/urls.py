from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path
from . import views

# 토큰은 헤더에 키:Authorization 밸류: Token xxxxxxxxxxxxxxxxxx 라는 규칙으로 보내야한다.
urlpatterns = [
    path("", views.Users.as_view()),
    path("@<str:username>", views.PublicUser.as_view()),
    path("me", views.Me.as_view()),
    path("change-password", views.ChangePassword.as_view()),
    path("log-in", views.LogIn.as_view()),
    path("log-out", views.LogOut.as_view()),
    path("token-login", obtain_auth_token),
    path("jwt-login", views.JWTLogIn.as_view()),
    path("github", views.GithubLogIn.as_view()),
    path("kakao", views.KakaoLogIn.as_view()),
]
