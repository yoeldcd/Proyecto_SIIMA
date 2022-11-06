
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from datetime import datetime

html_template_url = 'user_profile.html'

# page GET method invoked
def get(request : HttpRequest):
    
    user_profile = {
        'nickname': 'ADMIN',
        'picture_url': '/img/profile.png',
        'first_names': 'Yoel David',
        'sur_names': 'Correa Duke',
        'age': 23,
        'genere': 'male'
    }
    
    context = {
        'current_date': datetime.now,
        'profile_url': '/profile/user/',
        'user' : user_profile,
        'links':(
            {'href': '/tests/', 'text': 'analisis'},
        )
    }
    
    return HttpResponse(render(request, html_template_url, context))
    