from django.contrib import admin
from django.urls import path, re_path
from . import views
from . import models
from . import views as user_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('profile', user_views.profile, name='profile'),
    path('connect', user_views.connect, name='connect'),
    #path('register', user_views.register, name='register'),
    #path('login', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    #path('nouvelleliste', user_views.nouvelleListe, name='nouvelleListe'),
    path('edit/<int:listeId>', views.editListe, name='editListe'),
]