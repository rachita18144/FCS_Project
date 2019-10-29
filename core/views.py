from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from core.models import Groups, Friends, FriendTimelinePost, UserPosts, DirectMessages, GroupRequest, UserGroup, GroupNew, UpdateProfile, PagePosts, Pages,BalanceInfo
from core.models import MoneyRequests
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from django.contrib import messages
from sequences import get_next_value
from django.db.models import Count

user = None
grp_name = None
user_type = None

#TODO: Add google authentication(using OTP), add a new page

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
    global user_type 
    s=request.POST.__contains__('postcontent')
    if s:
        model=UserPosts()
        now = datetime.now()
        str=now.strftime("%Y-%m-%d %H:%M:%S")
        content=request.POST.get('postcontent')
        print(content)
        model.postContent=content
        model.postedBy= request.user.username
        model.postTime=str
        model.postedOn= request.user.username
        model.save()

    allposts=UserPosts.objects.filter(postedOn=request.user.username).order_by('-postTime')
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
    try:
       p1= BalanceInfo.objects.get(userid=user)
    except BalanceInfo.DoesNotExist:
        payment = BalanceInfo()
        payment.balance = 0
        payment.userid = user
        payment.save()
    type = v.user_type
    if type == "Casual":
        return render(request, 'user/home.html',{'allposts':allposts,'friend_count':friend_count,'group_count':group_count, 'a': True})
    else:
        return render(request, 'user/home.html',{'allposts':allposts,'friend_count':friend_count,'group_count':group_count, 'a': False})


#open friend profile and pass username of friend
@login_required(login_url='/accounts/login/')
def personProfile(request, username):
    if user:
        isFriend = checkIfAlreadyFriend(username, request.user.username)
        return render(request, 'user/friend_profile.html', {'username':username, 'isFriend':isFriend} )
    if grp_name:
        # return view(request, username)
        return view(request, username)

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
    allmsgs=(DirectMessages.objects.filter(sender=name)|DirectMessages.objects.filter(receiver=name).filter(sender=request.user.username)).order_by('time')
    print(allmsgs.count())
    return render(request,'user/directmessage.html',{'allmsgs':allmsgs,'friendname':name})

def friends(request):
    allfriends=Friends.objects.filter(person_user_name=request.user.username).order_by('friend_user_name')   
    return render(request, 'user/listfriends.html',{'allfriends':allfriends})

def viewprofile(request,name):
    isFriend = checkIfAlreadyFriend(name, request.user.username)
    s=request.POST.__contains__('post_text')
    if s:

        model=UserPosts()
        now = datetime.now()
        str=now.strftime("%Y-%m-%d %H:%M:%S")
        content=request.POST.get('post_text')
        print(content)
        model.postContent=content
        model.postedBy= request.user.username
        model.postedOn= name
        model.postTime=str
        model.save()

    allposts=UserPosts.objects.filter(postedOn=name).order_by('-postTime')
    print(allposts.count())
    return render(request, 'user/friend_profile.html', {'username':name, 'isFriend':isFriend,'allposts':allposts} )

def groups(request):
    allgroups=Groups.objects.filter(person_user_name=request.user.username).order_by('group_name')
    return render(request, 'user/listgroups.html',{'allgroups':allgroups})

def allUsers(request):
    allusers=User.objects.all
    return render(request, 'user/all_users.html', {'users':allusers, 'user_type':user_type})

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
            ph= request.POST.get('phno')
            length= len(ph)
            if length!=10:
                return render(request,'updateprofile/update.html',{'a':True})
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
            close="close"
            c= GroupNew.objects.filter(admin_id= user, privacy=close).count()
            privacy= request.POST.get('privacy')
            obj= UpdateProfile.objects.get(user_id= user)
            type= obj.user_type
            if type== 'PremiumSilver' and privacy== 'close':
                if c==2:
                    return render(request, 'group/creategroup.html', {'limit':True})
            elif type== 'PremiumGold'  and privacy== 'close':
                if c==4:
                    return render(request, 'group/creategroup.html', {'limit2': True})


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
    group_name=str(group).strip()
    user = request.user.id
    print(group_name)
    glist= GroupNew.objects.get(group_name= group_name)
    e= GroupNew.objects.filter(group_name= group_name).exists()
    print(e)
    print(glist.group_id)
   # gid1 = glist.values("group_id")
  #  gid = gid1[0]
    v=0
    p=0
    g_id1=0
   # id = list(gid)[0]
    #gid.get(id)
    status = GroupRequest.objects.filter(group_id = glist.group_id, user_id= user)
    ex= GroupRequest.objects.filter(group_id = glist.group_id, user_id= user).exists()
    bool1 = 3
    privacy= glist.privacy
   # privacy1= privacy[0]
   # p_id= list(privacy1)[0]
   # pid= privacy1.get(p_id)
    group_t= glist.group_type
  #  gt1=group_t[0]
  #  gt= list(gt1)[0]
  #  g_id= gt1.get(gt)
    if group_t == "premium":
        g_id1=1
    userg_exist= UserGroup.objects.filter(user_id= user, group_id=glist.group_id).exists()
    if userg_exist:
        joined= True
    else:
        joined= False
    if privacy=='open':
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
    t = UserGroup.objects.filter(user_id= user, group_id= glist.group_id).exists()
    l=[group_name,bool, v, p, joined, g_id1]
    return render( request,'group/viewgroup.html', {'l': l})

def join(request):
    userreq= GroupRequest()
    gname= request.GET.get("gname"," ")
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
    gname = request.GET.get("gname", " ")
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
    gname = request.GET.get("gname", "")
    i = 0;
    length = len(gname)
    group_name = ""

    while i != length:
        group_name += gname[i]
        i = i + 1
    print("hiiiiiii",group_name)
    glist = GroupNew.objects.get(group_name=str(group_name).strip())
   # g_privacy = glist.privacy
    amount = glist.amount
    return render(request, 'group/payment.html',{'gname':group_name, 'amount':amount})
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
    if request.method == "POST":
        pagename=request.POST.get('pagename')
        pagebio=request.POST.get('pagebio')
        print(pagename)
        print(pagebio)
        if pagename == '':
            messages.info(request,'Enter Page name')
            return redirect('createpage')
        else:
            model=Pages()
            model.page_name=pagename
            model.page_des=pagebio
            model.page_admin=request.user.username
            model.save()
            messages.info(request, 'Page Created!')
            return redirect('createpage')
    else:
        return render(request,'pages/create_page_form.html')

def paymentRequests(request):
    requests = MoneyRequests.objects.filter(friend_name= request.user.username).values()
    return render(request,'payment/payment_request.html',{'moneyrequests':requests})

def rejectRequest(request, request_id):
    MoneyRequests.objects.filter(request_id=request_id).delete()
    return paymentRequests(request)

def requestmoney(request,name):
    if name=="showlist":
        allfriends=Friends.objects.filter(person_user_name=request.user.username).order_by('friend_user_name')
        return render(request,'payment/show_friends.html',{'allfriends':allfriends})
    elif name=="requests":
        print("-----------")
        requests = MoneyRequests.objects.filter(friend_name= request.user.username).values()
        return render(request,'payment/payment_request.html',{'moneyrequests':requests})
    else:
        if request.method=="POST":
            amount_=request.POST.get('amount')
            if amount_=='':
                messages.info(request, 'Enter the amount!')
            else:
                model=MoneyRequests()
                model.friend_name=name
                model.amount=request.POST.get('amount')
                model.person_name=request.user.username
                model.save()
                messages.info(request, 'Request sent!')
        allfriends=Friends.objects.filter(person_user_name=request.user.username).order_by('friend_user_name')
        return render(request,'payment/show_friends.html',{'allfriends':allfriends})

def approve(request):
    gname= request.POST.get("gname", [])
    length=len(gname)
    k=[]
    str1=""
    i=0
    while gname[i]!=',':
        str1 += gname[i]
        i=i+1
    uid=""
    i=i+1
    while i!=length:
        uid+=gname[i]
        i=i+1
    print(str1)
    print(uid)
    glist = GroupNew.objects.get(group_name=str1)
   # gid1 = glist.values("group_id")
   # gid = gid1[0]
   # id = list(gid)[0]
    group_id = glist.group_id
    req= GroupRequest.objects.get(user_id= str(uid), group_id= group_id)
    req.request=1
    req.save()
    usergroup= UserGroup()
    usergroup.group_id= group_id
    usergroup.user_id= uid
    usergroup.save()
    return render(request, 'group/viewrequest.html',{'t_flag':True})

def payment1(request):
    gname= request.POST.get("gname","")
    i=0;
    length=len(gname)
    group_name=""

    while i!=length:
        group_name+=gname[i]
        i=i+1
    print(group_name)
    glist= GroupNew.objects.get(group_name= group_name)
    g_privacy= glist.privacy
    amount= glist.amount
    g_id= glist.group_id
    admin= glist.admin_id
    b = BalanceInfo.objects.get(userid=request.user.id)
    p = b.balance
    d = 0
   # num= Transaction.objects.get(userid= request.user.id)
  #  if num==15:
  #      return render(request,'user/home.html',{'num':True})
    if p != 0 and p>=amount:
        p1 = p - amount
        b.balance = p1
        b.save()
    else:
        d = 1
    if d==1:
        return render(request, 'user/home.html', {'d':d})
    if g_privacy=='open':
        u=UserGroup()
        u.group_id= g_id
        u.user_id= request.user.id
        u.save()
    else:
        u= GroupRequest()
        u.request=0
        u.user_id= request.user.id
        u.group_id= g_id
        u.admin_id= admin
        u.save()

    if g_privacy=='open':
        return render(request, 'user/home.html',{'join':True})
    else:
        return render(request, 'user/home.html', {'alert_flag1': True})
