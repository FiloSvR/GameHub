"""Account URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/

Examples:
    Function views
        1. Add an import:  from my_app import views
        2. Add a URL to urlpatterns:  path('', views.home, name='home')
    
    Class-based views
        1. Add an import:  from other_app.views import Home
        2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
    
    Including another URLconf
        1. Import the include() function: from django.urls import include, path
        2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include, reverse
from django.contrib.auth import views as auth_views
from .views import RegisterView, home_view, pick_group

app_name = 'accounts'

urlpatterns = [
    path('', home_view, name="home"),
    path('accounts/choosegroup', pick_group, name="choosegroup" ),
    path('accounts/register', RegisterView.as_view(template_name='accounts/register.html', success_url='home'), name='register'),
    path('accounts/login', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('accounts/logout', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    #path('accounts/', include('django.contrib.auth.urls')),
]