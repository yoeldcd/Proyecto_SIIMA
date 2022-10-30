from re import template
from django.http import HttpResponse, HttpRequest;
from django.template import Template, Context

root = 'siima/root/'
end = 0

# Miscelaneous

def open_url (req : HttpRequest):
    fullpath = root+req.path
    file = open(fullpath)
    resp = file.read()
    file.close()
    
    return HttpResponse(resp)
end

def render_template(url : str , values : dict):
    
    # opening source template
    html = open(root+url)
    template = Template(html.read());
    html.close();
    
    # rendering template context
    html = template.render(Context(values))
    print(str(html))

    return html
end
