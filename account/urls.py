from django.urls import path, re_path, include
from account import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    re_path(r'^login/?$', views.login, name="login"),
    re_path(r'^logout/?$', views.logout, name="logout"),
    re_path(r'^signup/?$', views.signup, name="signup"),
    re_path(r'^password_reset/$', auth_views.PasswordResetView.as_view(
        template_name='password_reset_form.html'), name='password_reset'),
    re_path(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_done.html'), name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    re_path(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'), name='password_reset_complete'),
]