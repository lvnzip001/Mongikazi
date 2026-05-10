from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("role/", views.role_select, name="role_select"),
    path("register/<str:role>/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("logout/confirm/", views.logout_confirm, name="logout_confirm"),
    path("password-reset/", views.password_reset_placeholder, name="password_reset"),
    path("pending/", views.account_pending, name="account_pending"),
]
