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
    path('profile/all_users',views.allUsers, name='allusers'),
    path('profile/updateprofile', views.update1, name='update1'),
    path('profile/update', views.update, name='update'),
    path('profile/viewrequest', views.viewrequest, name='viewrequest'),
    path('profile/creategroup', views.create1, name='createg'),
    path('profile/create' , views.create, name="create"),
    path('profile/view', views.view, name="view"),
    path('profile/join', views.join, name="join"),
    path('profile/join1', views.join1, name="join1"),
    path('profile/post', views.post, name="post"),
    path('profile/payment', views.payment, name="payment"),
    path('profile/viewrequest1', views.viewrequest1, name="viewrequest1"),
    path('profile/viewcontent', views.viewcontent, name="viewcontent"),
    path('profile/approve', views.approve, name="approve"),
    path('pages/<name>',views.listpages,name='pages'),
    path('createpage',views.createPage,name='createpage'),
    path('payment/requests',views.paymentRequests,name='paymentRequests'),
    path('payment/reject_request/<request_id>',views.rejectRequest,name='rejectrequest'),
]
