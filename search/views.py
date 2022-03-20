from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse
from github.GithubException import UnknownObjectException

from .models import GitHubUser, GitHubRepository, Skill, Search
from .forms import SearchForm
import math


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


def results(request, by, query, page):
    def reverse_url_kwargs(page_number):
        return {
            'by': by,
            'query': query,
            'page': page_number,
        }
    search = Search(query=query, by=by)
    paginated_list = search.search(query, by)
    results_page = paginated_list.get_page(page)
    page_count = math.ceil(paginated_list.totalCount / 30)
    if page > page_count:
        url = reverse("search:results", kwargs=reverse_url_kwargs(1))
        return redirect(url)
    pagination = {
        page_number: reverse("search:results", kwargs=reverse_url_kwargs(page_number)) if (page_number != page) else None
        for page_number in range(max(page - 2, 1), min(page + 3, page_count))
    }
    context = {
        'results': results_page,
        'pagination_dict': pagination
    }
    html_template = loader.get_template('search/results.html')
    return HttpResponse(html_template.render(context, request))
