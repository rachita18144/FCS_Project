from django.contrib import admin
from core.models import Friends, Groups, FriendTimelinePost, GroupNew, GroupRequest, UpdateProfile, UserGroup, Pages, PagePosts
from core.models import MoneyRequests, DirectMessages, UserPosts

admin.site.register(Friends)
admin.site.register(Groups)
admin.site.register(FriendTimelinePost)
admin.site.register(GroupNew)
admin.site.register(GroupRequest)
admin.site.register(UserGroup)
admin.site.register(UpdateProfile)
admin.site.register(Pages)
admin.site.register(PagePosts)
admin.site.register(MoneyRequests)
admin.site.register(DirectMessages)
admin.site.register(UserPosts)