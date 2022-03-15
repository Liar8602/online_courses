from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from .forms import StudentForm, StudentProfileForm
from settings.settings import django_logger


def index(request):
    context = {'active': "home"}
    return render (request, 'index.html', context=context)


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


def user_login(request):
    errors_string = None
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                errors_string = 'WRONG ACCOUNT'
        else:
            django_logger.info(f'invalid login: "{username}" password: "{password}"')
            errors_string = 'INVALID USERNAME OR PASSWORD!'
    
    context = {'active': "login", 'errors': errors_string}
    return render(request, 'login.html', context)


def user_register(request):
    registered = False
    errors_string = None

    if request.method == "POST":
        user_form = StudentForm(data=request.POST)
        profile_form = StudentProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']

            profile.save()
            registered = True
        else:
            all_errors = []
            for err_list in user_form.errors.values():
                all_errors.append(' '.join(err_list))
            for err_list in profile_form.errors.values():
                all_errors += ' '.join(err_list)
            errors_string = ' '.join(all_errors)
    else:
        registered = True if request.user.username else False
        user_form = StudentForm()
        profile_form = StudentProfileForm()
    
    context = {
        'active': 'register',
        'errors': errors_string,
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered
    }
    return render(request, 'registration.html', context=context)
