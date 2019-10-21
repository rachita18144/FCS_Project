from django.db import models

class Friends(models.Model):
    person_user_name = models.CharField(max_length=30)
    friend_user_name = models.CharField(max_length=30)

    class Meta:
        unique_together = (("person_user_name", "friend_user_name"),)

    def __str__(self):
        return self.friend_user_name

#class Groups(models.Model):
#    created_by = models.CharField(max_length=30)
#    group_name = models.CharField(max_length=30)

class Groups(models.Model):
    person_user_name = models.CharField(max_length=30)
    group_name = models.CharField(max_length=60)

    def __str__(self):
        return self.group_name

    class Meta:
        unique_together = (("person_user_name", "group_name"),)

class FriendTimelinePost(models.Model):
    person_user_name = models.CharField(max_length=30)
    friend_user_name = models.CharField(max_length=30)
    post_content = models.TextField()

class UserPosts(models.Model):
    user_id = models.CharField(max_length=20)
    postContent = models.TextField()
    postTime = models.DateTimeField()

    def __str__(self):
        return self.postContent

    class Meta:
        db_table = 'UserPosts'

class DirectMessages(models.Model):
    sender= models.CharField(max_length=20)
    receiver= models.CharField(max_length=20)
    msg_content=models.TextField()
    time=models.DateTimeField()
    status=models.BooleanField()

    def __str__(self):
        return self.msg_content

class Pages(models.Model):
    page_name= models.CharField(max_length=30, unique=True)
    page_des=models.CharField(max_length=100)
    page_admin=models.CharField(max_length=30)

class PagePosts(models.Model):
    page_name=models.CharField(max_length=30)
    post_content=models.TextField()
    postTime=models.DateTimeField()

    def __str__(self):
        return self.msg_content
