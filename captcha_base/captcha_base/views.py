from django.shortcuts import render, redirect
from django.contrib import messages
from captcha.views import recaptcha_verification


def home(request):
    return render(request, 'index.html')


def subbmit_name(request):
    if request.method == 'POST':


        success = recaptcha_verification(request)
        if not success:
            messages.error(request, "Recaptcha verification failed. Please try again.")
            return render(request, 'page/login.html')

        name = request.POST.get('name_field')
        messages.success(request, f'Hello {name}, successfully submitted')
        return redirect('home')
    messages.error(request, 'Please enter your name, with post request')
    return redirect('home')