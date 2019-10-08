from django.contrib import admin
from django.urls import path, include
from social_site.core import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    #the default page
    path('', views.loginSignup, name='loginSignup'),
    path('profile/home', views.home, name='home'),
]
