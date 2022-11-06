
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from datetime import datetime

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