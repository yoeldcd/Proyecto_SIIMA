from siima.endpoint import tools
from django.http import HttpRequest, HttpResponse

end = 0
root = 'siima/root/'
html_template_url = root + 'user_profile.html'

# page GET method invoked
def get(request : HttpRequest):
    
    user = {
        'nickname': 'ADMIN',
        'picture_url': '/img/profile-log.png',
        'first_names': 'Yoel David',
        'sur_names': 'Correa Duke',
        'age': 23,
        'genere': 'male'
    }
    
    context = {
        'user' : user
    }
    
    return HttpResponse(tools.render_template(html_template_url, context))
end