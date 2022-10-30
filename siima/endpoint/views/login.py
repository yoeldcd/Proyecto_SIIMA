
from endpoint import tools
from django.http import HttpRequest, HttpResponse

end = 0

def get(request : HttpRequest):
    
    user = {
        'nickname': 'ADMIN',
        'picture_url': 'root/img/profile-log.png',
        'first_names': 'Yoel David',
        'sur_names': 'Correa Duke',
        'age': 23,
        'genere': 'male'
    }
    
    context = {
        'user' : user
    }
    
    return HttpResponse(tools.render_template('admin-profile.html', context))
end