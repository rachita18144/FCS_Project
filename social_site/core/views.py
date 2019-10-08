from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

def loginSignup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        #print(form)
        print(form.is_valid())
        if form.is_valid():
            print("here")
            form.save()
            return redirect('loginSignup')
    else:
        form = UserCreationForm()

    return render(request, 'registration/loginSignup.html', {
        'form' : form
    })

@login_required(login_url='/accounts/login/')
def home(request):
    return render(request, 'user/home.html')