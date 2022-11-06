
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from datetime import datetime

html_template_url = 'user_profile.html'

# page GET method invoked
def get(request : HttpRequest):
    
    user_profile = {
        'id': 'hash256',
        'nickname': 'user6267',
        'picture_url': '/img/user6267.jpg',
        'name': 'Yoel',
        'name2': 'David',
        'surname': 'Correa',
        'surname2': 'Duke',
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
    