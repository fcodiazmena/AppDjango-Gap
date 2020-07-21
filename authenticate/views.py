from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseRedirect
from django.urls import reverse


def iniciarSesion(request):
    context = {}
    template_name = 'authenticated/login.html'
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            context['msg_error'] = 'Error de login'
    return render(request, template_name, context)


def salirSesion(request):
    print('cerrar')
    context = {}
    template_name = 'authenticated/logout.html'

    logout(request)

    return HttpResponseRedirect(reverse('login'))
