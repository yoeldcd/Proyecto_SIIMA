
from datetime import datetime
from siima.endpoint import tools
from django.http import HttpRequest, HttpResponse

end = 0
html_template_url = 'siima/templates/main_layout.html'

# page GET method invoked
def get(request : HttpRequest):
    
    context = {
        'current_date': datetime.now            
    }
    
    return HttpResponse(tools.render_template(html_template_url, context))
end