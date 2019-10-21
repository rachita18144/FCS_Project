from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from core.models import Groups, Friends, FriendTimelinePost, UserPosts, DirectMessages,Pages,PagePosts
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

user = None
grp_name = None

#TODO: Add google authentication(using OTP), add a new page
def loginSignup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        #print(form)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            return redirect('loginSignup')
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
                grp_name = Groups.objects.get(group_name=grp_search_query)
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
    return render(request, 'user/home.html',{'allposts':allposts,'friend_count':friend_count,'group_count':group_count})


#open friend profile and pass username of friend
@login_required(login_url='/accounts/login/')
def personProfile(request, username):
    if user:
        isFriend = checkIfAlreadyFriend(username, request.user.username)
        return render(request, 'user/friend_profile.html', {'username':username, 'isFriend':isFriend} )
    if grp_name:
        return render(request, 'user/group_page.html', {'group_name':username} )

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