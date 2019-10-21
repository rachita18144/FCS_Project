from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from core.models import Groups, Friends, FriendTimelinePost, UserPosts, DirectMessages, GroupRequest, UserGroup, GroupNew, UpdateProfile, PagePosts, Pages
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.contrib import messages
from sequences import get_next_value
from django.db.models import Count

user = None
grp_name = None

#TODO: Add google authentication(using OTP), add a new page
#TODO: Search group from group name

def loginSignup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        #print(form)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'registration/loginSignup.html', {
        'form' : form
    })

#handle blank search query
@login_required(login_url='/accounts/login/')
def search(request):
    global user
    global grp_name
    if request.method=='POST':
        if 'srch' in request.POST:
            search_query = request.POST['srch'] 
            if search_query:
                grp_name=None
                try:
                    user = User.objects.get(username=search_query)
                except User.DoesNotExist:
                    user = None
                if user:
                    return render(request, 'user/search.html', {'sr':user})
                else:
                    return render(request, 'user/search.html', {'messages':'Not Found'})

        grp_search_query = request.POST['grp_search']
        if grp_search_query:
            user=None
            try:
                grp_name = GroupNew.objects.get(group_name=grp_search_query)
            except ObjectDoesNotExist:
                grp_name = None
            if grp_name:
                return render(request, 'user/search.html', {'gr':grp_name})
            else:
                return render(request, 'user/search.html', {'messages':'Not Found'})
    #handle post request also
    return render(request, 'user/search.html')

@login_required(login_url='/accounts/login/')
def home(request):
    s=request.POST.__contains__('postcontent')
    if s:
        model=UserPosts()
        now = datetime.now()
        str=now.strftime("%Y-%m-%d %H:%M:%S")
        content=request.POST.get('postcontent')
        print(content)
        model.postContent=content
        model.user_id= request.user.username
        model.postTime=str
        model.save()

    allposts=UserPosts.objects.filter(user_id=request.user.username).order_by('-postTime')
    friend_count=Friends.objects.filter(person_user_name=request.user.username).count()
    group_count=Groups.objects.filter(person_user_name=request.user.username).count()

    user = request.user.id
    g = UpdateProfile()
    try:
        u = UpdateProfile.objects.get(user_id=user)
    except UpdateProfile.DoesNotExist:
        g.user_id = user
        b = "Casual"
        g.user_type = b
        g.save()
    v = UpdateProfile.objects.get(user_id=user)
    type = v.user_type
    if type == "Casual":
        return render(request, 'user/home.html',{'allposts':allposts,'friend_count':friend_count,'group_count':group_count, 'alert_flag': True})
    else:
        return render(request, 'user/home.html',{'allposts':allposts,'friend_count':friend_count,'group_count':group_count, 'alert_flag': False})

#open friend profile and pass username of friend
@login_required(login_url='/accounts/login/')
def personProfile(request, username):
    if user:
        isFriend = checkIfAlreadyFriend(username, request.user.username)
        return render(request, 'user/friend_profile.html', {'username':username, 'isFriend':isFriend} )
    if grp_name:
        return view(request, username)
        #return render(request, 'user/group_page.html', {'group_name':username} )

@login_required(login_url='/accounts/login/')
def addFriend(request):
    #add friend to model logic
    if request.method == 'POST':
        uname = request.POST.get("friend_user_name")
        saveFriendDataToDb(uname, request.user.username)
        data = {
            "msg":"success"
        }
        return JsonResponse(data)

def saveFriendDataToDb(funame, username):
    f = Friends(person_user_name=username, friend_user_name=funame)
    f.save()

def checkIfAlreadyFriend(friend_user_name, self_username):
    try:
        friend = Friends.objects.get(person_user_name=self_username, friend_user_name=friend_user_name)
    except ObjectDoesNotExist:
        friend = None
    if friend:
        return True
    else:
        return False

def removeFriend(request):
    if request.method == 'POST':
        uname = request.POST.get("friend_user_name")
        Friends.objects.filter(person_user_name=request.user.username, friend_user_name=uname).delete()
        data = {
            "msg":"success"
        }
        return JsonResponse(data)

def postTimeline(request):
    if request.method == 'POST':
        uname = request.POST.get("friend_user_name")
        post_content = request.POST.get("post_content")
        f = FriendTimelinePost(person_user_name=request.user.username, friend_user_name=uname, post_content=post_content)
        f.save()
        data = {
            "msg":"success"
        }
        return JsonResponse(data)

def directmessage(request,name):
    print(name)
    s=request.POST.__contains__('msgcontent')
    if s:
        model=DirectMessages()
        now = datetime.now()
        str=now.strftime("%Y-%m-%d %H:%M:%S")
        content=request.POST.get('msgcontent')
        model.msg_content=content
        model.sender= request.user.username
        model.receiver= name
        model.time=str
        model.status=False
        model.save()
    allmsgs=(DirectMessages.objects.filter(sender=name)|DirectMessages.objects.filter(receiver=name)).order_by('time')
    print(allmsgs.count())
    return render(request,'user/directmessage.html',{'allmsgs':allmsgs,'friendname':name})

def friends(request):
    allfriends=Friends.objects.filter(person_user_name=request.user.username).order_by('friend_user_name')
    return render(request, 'user/listfriends.html',{'allfriends':allfriends})

def viewprofile(request,name):
    isFriend = checkIfAlreadyFriend(name, request.user.username)
    return render(request, 'user/friend_profile.html', {'username':name, 'isFriend':isFriend} )

def groups(request):
    allgroups=Groups.objects.filter(person_user_name=request.user.username).order_by('group_name')
    return render(request, 'user/listgroups.html',{'allgroups':allgroups})

def allUsers(request):
    allusers=User.objects.all
    return render(request, 'user/all_users.html', {'users':allusers})

def update1(request):
    return render(request, 'updateprofile/update.html')

def create1(request):
    return render(request, 'group/creategroup.html')

def viewrequest(request):
    return render(request, 'group/viewrequest.html')

def update(request):
    if request.method == 'POST':
        if request.POST.get('fname') and request.POST.get('lname') and request.POST.get('bio1')  and request.POST.get('phno'):
            post = UpdateProfile()
            user = request.user.id
            u = UpdateProfile.objects.get(user_id = user)
            if u:
                u.user_id = user
                u.First_name = request.POST.get('fname')
                u.Last_name = request.POST.get('lname')
                u.Bio = request.POST.get('bio1')
                u.Privacy_setting = request.POST.get('op1')
                u.save()
            else:
                post.user_id = user
                post.First_name = request.POST.get('fname')
                post.Last_name = request.POST.get('lname')
                post.Bio = request.POST.get('bio1')
                post.Privacy_setting = request.POST.get('op1')
                post.save()
            return render(request, 'updateprofile/update.html')

        else:
          #  messages.info(request, 'Please fill all the fields')
            return render(request, 'updateprofile/update.html' , {'alert_flag': True})


def create(request):
    if request.method == 'POST':
        if request.POST.get('groupname'):
            p = GroupNew()
            user = request.user.id
            g = request.POST.get('groupname')
            t=1

            if GroupNew.objects.filter( group_name = g).exists():
                return render(request, 'group/creategroup.html', {'alert_flag': True})
            else:
                val =get_next_value('create', initial_value=1001)
                p.group_id = val
                p.group_name = request.POST.get('groupname')
                p.admin_id = user
                p.privacy = request.POST.get('privacy')
                p.group_type = request.POST.get('grouptype')
                p.amount = request.POST.get('amount')
                p.save()
                usergroup= UserGroup()
                usergroup.user_id= user
                usergroup.group_id= val
                usergroup.save()

                return render(request, 'group/creategroup.html', {'alert_flag1': True})

        else:
           # messages.info(request, 'Please fill all the fields')
            return render(request, 'group/creategroup.html', {'alert_flag2': True})


def view(request, group):
    group_name=group
    user = request.user.id
    glist= GroupNew.objects.filter(group_name= group_name)
    gid1 = glist.values("group_id")
    gid = gid1[0]
    v=0
    p=0
    g_id1=0
    id = list(gid)[0]
    status = GroupRequest.objects.filter(group_id = gid.get(id), user_id= user)
    ex= GroupRequest.objects.filter(group_id = gid.get(id), user_id= user).exists()
    bool1 = 3
    privacy= glist.values("privacy")
    privacy1= privacy[0]
    p_id= list(privacy1)[0]
    pid= privacy1.get(p_id)
    group_t= glist.values("group_type")
    gt1=group_t[0]
    gt= list(gt1)[0]
    g_id= gt1.get(gt)
    if g_id == "premium":
        g_id1=1
    userg_exist= UserGroup.objects.filter(user_id= user, group_id= gid.get(id)).exists()
    if userg_exist:
        joined= True
    else:
        joined= False
    if pid=='open':
        p= 1
    else:
        p= 0
    if ex:
        v=1
        statuslist = status.values("request")
        status1= statuslist[0]
        id1= list(status1)[0]
        val= status1.get(id1)
        if val == 1:
            bool= True
        else:
            bool= False
    else:
        bool= False
  #  count = UserGroup.objects.filter(group_id= gid.get(id)).count()
    t = UserGroup.objects.filter(user_id= user, group_id= gid.get(id)).exists()
    l=[group_name,bool, v, p, joined, g_id1]
    return render( request,'group/viewgroup.html', {'l': l})

def join(request):
    userreq= GroupRequest()
    gname= request.POST.get("gname"," ")
    glist = GroupNew.objects.filter(group_name=gname)
    gid1 = glist.values("group_id")
    aid1= glist.values("admin_id")
    aid= aid1[0]
    a_id= list(aid)[0]
    admin_id= aid.get(a_id)
    gid = gid1[0]
    id = list(gid)[0]
    group_id= gid.get(id)
    userreq.admin_id= admin_id
    userreq.request= 0
    userreq.group_id= group_id
    userreq.user_id= str(request.user.id)
    userreq.save()
    return render(request, 'user/home.html', {'alert_flag1': True})

def join1(request):
    gname = request.POST.get("gname", " ")
    glist = GroupNew.objects.filter(group_name=gname)
    gid1 = glist.values("group_id")
    gid = gid1[0]
    id = list(gid)[0]
    group_id = gid.get(id)
    user= str(request.user.id)
    ugroup= UserGroup()
    ugroup.user_id= user
    ugroup.group_id= group_id
    ugroup.save()
    return render(request, 'user/home.html', {'join': True})

def post(request):
    name= request.POST.get("gname","")
    print(name)
    return render(request, 'group/viewgroup.html', {'l':name})

def payment(request):
    return render(request, 'group/payment.html')
def viewrequest1(request):
    user= request.user.id
    glist= GroupNew.objects.filter(admin_id= user)
    gval= glist.values("group_name")
    length= len(gval)
    l=[]
    for i in range(length):
        gval1= gval[i]
        g= list(gval1)[0]
        l.append(gval1.get(g))
    return render(request,'group/viewrequest.html',{'l':l})

def viewcontent(request):
    gname = request.POST.get("gname", "")
    #print("hii")
    #print(gname)
    glist = GroupNew.objects.filter(group_name=gname)
    gid1 = glist.values("group_id")
    gid = gid1[0]
    id = list(gid)[0]
    group_id = gid.get(id)
    reqlist= GroupRequest.objects.filter(group_id=group_id, request=0, admin_id= request.user.id)
    rlist1= reqlist.values("user_id")

    length= len(rlist1)
    l=[]
    k3=[]
    for i in range(length):
        rval1= rlist1[i]
        g= list(rval1)[0]
        l.append(rval1.get(g))
    k=[]
    k1=[]
    for j in l:
        val= UpdateProfile.objects.get(user_id= j)
        uname= val.First_name
       # ulist= uname[0]
       # u= list(ulist)[0]
       # u1= ulist.get(u)
        k.append(j)
        k1.append(uname)
        k3.append(gname)
    z= zip(k,k1,k3)
    return render(request, 'group/viewrequest.html',{'k':z})
def approve(request):
    gname= request.POST.get("gname", [])
    length=len(gname)
    k=[]
    str1=""
    for i in range(length-1):
        str1 += gname[i]
    uid= gname[length-1]
    glist = GroupNew.objects.filter(group_name=str1)
    gid1 = glist.values("group_id")
    gid = gid1[0]
    id = list(gid)[0]
    group_id = gid.get(id)
    req= GroupRequest.objects.get(user_id= str(uid), group_id= group_id)
    req.request=1
    req.save()
    usergroup= UserGroup()
    usergroup.group_id= group_id
    usergroup.user_id= uid
    usergroup.save()
    return render(request, 'group/viewrequest.html',{'t_flag':True})

def listpages(request,name):
    if name=="show":
        allpages=Pages.objects.filter().order_by('page_name')
        return render(request,'pages/listpages.html',{'allpages':allpages})
    else:
        s=request.POST.__contains__('postcontent')
        print(s)
        if s:
            model=PagePosts()
            now = datetime.now()
            str=now.strftime("%Y-%m-%d %H:%M:%S")
            content=request.POST.get('postcontent')
            print(content)
            model.post_content=content
            model.page_name=name
            model.postTime=str
            model.save()
        page=Pages.objects.filter(page_name=name)
        allposts=PagePosts.objects.filter(page_name=name).order_by('-postTime')
        print(allposts.count())
        return render(request,'pages/pagelayout.html',{'page':page,'pagename':name,'allposts':allposts})

def createPage(request):
    return render(request,'pages/create_page_form.html')

def paymentRequests(request):
    return render(request,'payment_request.html')
