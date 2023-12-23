from django.http import HttpResponse
from django.shortcuts import redirect, render

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        
        if request.user.is_authenticated and request.user.is_applicant:
            return redirect('applicant_home')
        elif request.user.is_authenticated and request.user.is_tupadmin:
            return redirect('tupadmin_home')
        elif request.user.is_authenticated and request.user.is_interviewer:
            return redirect('interviewer_home')
        elif request.user.is_authenticated and request.user.is_nurse:
            return redirect('nurse_home')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func