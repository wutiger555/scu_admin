from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template

def responseHome(request):
    template = get_template('index.html')
    html = template.render(locals())
    return HttpResponse(html)

def responseLogin(request):
    template = get_template('login.html')
    html = template.render(locals())
    return HttpResponse(html)