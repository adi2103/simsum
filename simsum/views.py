import fb_api, t_api
from django.shortcuts import redirect
from django.shortcuts import render
from . import matcher
import logging
import json, re
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def index(request):
    return render(request, 'simsum/index.html')

def result(request):

    if request.method == 'GET' or request.method == 'POST' and not request.body:
        return redirect('index')

    fb_UserName = request.POST['fb_username']
    t_UserName = request.POST['t_username']

    context = {
        'fb_username': fb_UserName,
        't_UserName': t_UserName,
        'similarity': 0.0,
        'error_message': []
    }

    fb_pattern = re.compile(r'^([a-zA-Z0-9.]+)')
    t_pattern = re.compile(r'^([a-zA-Z0-9_]+)')

    if not fb_pattern.match(fb_UserName).group(0) == fb_UserName:
        context['error_message'].append("Facebook username invalid")
    if not t_pattern.match(t_UserName).group(0) == t_UserName:
        context['error_message'].append("Twitter username invalid")
    if context['error_message']:
        return render(request, 'simsum/index.html', context)

    base = "https://graph.facebook.com/v2.7"
    node = "/%s" % fb_UserName
    parameters = "?access_token=%s" % (fb_api.access_token)
    url = base + node + parameters
    data = json.loads(fb_api.request_until_succeed(url))
    if not data['id']:
        context['error_message'] = ["Facebook username doesn't exist."]

    try:
        data = t_api.api.get_user(t_UserName)
    except Exception, e:
        context['error_message'].append(e)

    if context['error_message']:
        return render(request, 'simsum/index.html', context)

    context['similarity'] = matcher.similarity(fb_UserName, t_UserName)
    return render(request, 'simsum/result.html', context)
