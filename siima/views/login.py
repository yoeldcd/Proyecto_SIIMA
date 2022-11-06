
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from datetime import datetime

from siima.views import user_profile
from siima.views import worker_profile
from siima.views import admin_profile

html_template_url = 'login.html'

# page GET method invoked
def get(request : HttpRequest):
    
    user_profile = None
    
    context = {
        'current_date': datetime.now,
        'profile_url': '/profile/user/',
        'user': user_profile,         
        'links':(
            {'href': '/profile', 'text': 'profile'},
            {'href': '/tests', 'text': 'test'},
        )
    }
    
    return HttpResponse(render(request, html_template_url, context))

def start(request : HttpRequest, id : str):
    
    if (id == 'root6267'):
        return admin_profile.get(request)
    elif (id == 'worker6267'):
        return worker_profile.get(request)
    else:
        return user_profile.get(request)
        