from django.urls import path
from .views.login import login_view
from .views.logout import logout_view
from .views.register import register_view

urlpatterns =[
    path("login/", login_view, name="login_view"),
    path("logout/", logout_view, name="logout_view"),
    path("register/", register_view, name="register_view")
]
