from django.http import HttpResponse
from django.template import loader


def index(request):
    context = {}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))
