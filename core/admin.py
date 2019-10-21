from django.contrib import admin
from core.models import Friends, Groups, FriendTimelinePost, GroupNew, GroupRequest, UpdateProfile, UserGroup

admin.site.register(Friends)
admin.site.register(Groups)
admin.site.register(FriendTimelinePost)
admin.site.register(GroupNew)
admin.site.register(GroupRequest)
admin.site.register(UserGroup)
admin.site.register(UpdateProfile)
