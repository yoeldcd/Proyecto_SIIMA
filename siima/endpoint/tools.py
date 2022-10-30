from re import template
from django.http import HttpResponse, HttpRequest;
from django.template import Template, Context

end = 0

# Miscelaneous

def open_css_url (req : HttpRequest):
    fullpath = req.path
    file = open(fullpath)
    resp = file.read()
    file.close()
    
    print(fullpath)
    
    return HttpResponse(resp, content_type = 'text/css')
end

def open_js_url (req : HttpRequest):
    fullpath = req.path
    file = open(fullpath)
    resp = file.read()
    file.close()
    
    print(fullpath)
    
    return HttpResponse(resp, content_type = 'text/js')
end


def render_template(url : str , values : dict):
    
    # opening source template
    html = open(url)
    template = Template(html.read());
    html.close();
    
    # rendering template context
    return template.render(Context(values))
end
