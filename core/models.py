from django.db import models

class Friends(models.Model):
    person_user_name = models.CharField(max_length=30)
    friend_user_name = models.CharField(max_length=30)

    class Meta:
        unique_together = (("person_user_name", "friend_user_name"),)

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
    postedBy = models.CharField(max_length=20)
    postContent = models.TextField()
    postTime = models.DateTimeField()
    postedOn= models.CharField(max_length=20)

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

class UpdateProfile(models.Model):
    user_id = models.CharField(max_length=250, default=" default ")
    First_name = models.CharField(max_length=250, default=" ")
    Last_name = models.CharField(max_length=250, default=" ")
    Bio = models.CharField(max_length=850, default=" ")
    Privacy_setting = models.CharField(max_length=250, default="public")
    Phone_number = models.IntegerField(default=0000000000)
    user_type = models.CharField(max_length=250, default="Casual")

    def __str__(self):
        return "%s %s %s %s" % (self.First_name, self.Last_name, self.Bio, self.Privacy_setting)


class GroupNew(models.Model):
    group_id = models.IntegerField(default=0)
    group_name = models.CharField(max_length=250)
    admin_id = models.CharField(max_length=250)
    privacy = models.CharField(max_length=250)
    group_type = models.CharField(max_length=250)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return " %s %s %s " % (self.group_name, self.admin_id, self.privacy)


class GroupRequest(models.Model):
    group_id = models.IntegerField(default=0)
    request = models.IntegerField(default=0)
    user_id = models.CharField(max_length=250)
    admin_id = models.CharField(max_length=250, default=0)


class UserGroup(models.Model):
    user_id = models.CharField(max_length=250)
    group_id = models.IntegerField(default=0)

class Pages(models.Model):
    page_name= models.CharField(max_length=30, unique=True)
    page_des=models.CharField(max_length=100)
    page_admin=models.CharField(max_length=30)

class PagePosts(models.Model):
    page_name=models.CharField(max_length=30)
    post_content=models.TextField()
    postTime=models.DateTimeField()

    def __str__(self):
        return self.post_content

class MoneyRequests(models.Model):
    request_id=models.AutoField(primary_key=True)
    friend_name=models.CharField(max_length=30)
    person_name=models.CharField(max_length=30)
    amount=models.IntegerField(default=0)

class BalanceInfo(models.Model):
    balance = models.IntegerField(default=0)
    userid = models.CharField(max_length= 50  , default = 0)
    def __str__(self):
        return self.userid
