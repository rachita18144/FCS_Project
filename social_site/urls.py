from django.contrib import admin
from django.urls import path, include, re_path
from core import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    #the default page
    path('', views.loginSignup, name='loginSignup'),
    path('profile/home', views.home, name='home'),
    path('profile/search', views.search, name='search'),
    path('profilePage/<username>', views.personProfile, name='personProfilePage'), 
    path('profile/friends/add_friend', views.addFriend, name='addFriend'), 
    path('profile/friends/delete_friend', views.removeFriend, name='removeFriend'), 
    path('profile/friends/post', views.postTimeline, name='postTimeline'), 
    path('dm/<name>',views.directmessage,name='dm'),
    path('profilepage/<name>',views.viewprofile,name='profilepage'),
    path('profile/friends',views.friends),
    path('profile/groups',views.groups),
    path('pages/<name>',views.listpages,name='pages'),
    path('createpage',views.createPage,name='createpage')
]
