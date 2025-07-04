from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('signup/email-confirmation/<str:uidb64>/', views.email_confirmation, name='email_confirmation'),
    path('signup/email-confirmed/<str:uidb64>/<str:token>/', views.email_confirmed, name='email_confirmed'),
    path('signup/email-resend/<str:uidb64>/', views.email_resend, name='email_resend'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('reset/',
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html',
            email_template_name='password_reset_email.html',
            subject_template_name='password_reset_subject.txt'
            ),
        name='password_reset'),
    path('reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),
    path('settings/password/', auth_views.PasswordChangeView.as_view(template_name='password_change.html'),
        name='password_change'),
    path('settings/password/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
        name='password_change_done'),
    path('settings/account/', views.UserUpdateView.as_view(), name='my_account'),
    # path('settings/account/', views.UserSettings.as_view(), name='my_account'),
    # path('settings/account/', views.ClientUpdateView.as_view(), name='my_account'),
    # path('settings/account/', views.user_update, name='my_account'),
]
