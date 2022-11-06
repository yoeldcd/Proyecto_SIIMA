
from django.http import HttpRequest, HttpResponse
from siima.views import user_profile;

def get(request : HttpRequest):
    return user_profile.get(request)


    
    