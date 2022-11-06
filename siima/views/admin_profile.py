from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from datetime import datetime

html_template_url = 'worker_profile.html'

# page GET method invoked
def get(request : HttpRequest):
    
    worker_profile = {
        'id': 'hash256',
        'nickname': 'root_user6267',
        'picture_url': '/img/user6267.jpg',
        'name': 'Yoel',
        'name2': 'David',
        'surname': 'Correa',
        'surname2': 'Duke',
        'age': 23,
        'genere': 'male',
        'role': 'admin',
        'permissions': ['r','e','a','d','s']
    }
    
    context = {
        'current_date': datetime.now,
        'profile_url': '/profile/admin/',
        'user' : worker_profile,
        'worker' : worker_profile,
        'links':(
            {'href': '/users/', 'text': 'usuarios'},
            {'href': '/events/', 'text': 'eventos'}
        )
    }
    
    return HttpResponse(render(request, html_template_url, context))
    