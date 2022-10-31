
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from datetime import datetime

end = 0
html_template_url = 'login.html'

# page GET method invoked
def get(request : HttpRequest):
    
    context = {
        'current_date': datetime.now,
        'profile_page_url':'/profile/&user=\'userID\'',
        'user':{
            'nickname': 'NO NAME',
            'picture_url': 'img/profile.png'
        },         
        'links':(
            {'href': '/profile', 'text': 'profile'},
            {'href': '/tests', 'text': 'test'},
        )
    }
    
    return HttpResponse(render(request, html_template_url, context))
end