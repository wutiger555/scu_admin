from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt 
def responseHome(request):
    template = get_template('index.html')
    html = template.render(locals())
    return HttpResponse(html)

@csrf_exempt 
def responseLogin(request):
    template = get_template('login.html')
    html = template.render(locals())
    return HttpResponse(html)

@csrf_exempt 
def stream_response(request):
    if request.method == 'POST':
        if request.POST.get('id', False):
            m = '<a> id=' + str(request.POST['id']) +' <br>password:' + str(request.POST['passwd'])+'</a>'
            # resp = StreamingHttpResponse(stream.streamx(m))
        return HttpResponse(m)