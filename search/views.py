from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from .models import Search
from .forms import SearchForm


def index(request):
    form = SearchForm(request.POST or None)
    context = {
        "form": form,
        "form_received": False,
    }
    if form.is_valid():
        search = form.save(commit=False)
        return redirect(search)
    html_template = loader.get_template('search/search.html')
    return HttpResponse(html_template.render(context, request))


def results(request, by, query):
    search = Search(query=query, by=by)
    context = {
        'results': [search.get_user('yigityalin')] * 2
    }
    html_template = loader.get_template('search/results.html')
    return HttpResponse(html_template.render(context, request))
