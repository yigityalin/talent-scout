from collections import Counter
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse
from .models import GitHubUser, GitHubRepository, Search
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
    paginated_list, return_type = search.search(query, by)
    page_count = math.ceil(paginated_list.totalCount / 30)
    if page > page_count:
        url = reverse("search:results", kwargs=reverse_url_kwargs(1))
        return redirect(url)
    results_page = paginated_list.get_page(page - 1)
    if return_type == GitHubRepository:
        results_page = list(set(repo.owner for repo in results_page))
    user_page_urls = [reverse('search:user', kwargs=dict(login=user.login)) for user in results_page]
    pagination = {
        page_number: reverse("search:results", kwargs=reverse_url_kwargs(page_number)) if (page_number != page) else None
        for page_number in range(max(page - 2, 1), min(page + 3, page_count))
    }
    context = {
        'results': zip(results_page, user_page_urls),
        'pagination_dict': pagination
    }
    html_template = loader.get_template('search/results.html')
    return HttpResponse(html_template.render(context, request))


def user_details(request, login):
    github_user = Search().get_user(login)
    paginated_repos = github_user.get_repos()
    page_count = math.ceil(paginated_repos.totalCount / 30)
    github_repos_list = []
    languages = Counter()
    for page in range(page_count):
        for repo in paginated_repos.get_page(page):
            languages.update(repo.get_languages())
            github_repos_list.append(repo)
    context = {
        'github_user': github_user,
        'github_user_languages': languages,
        'github_repos_list': github_repos_list,
    }
    html_template = loader.get_template('search/user.html')
    return HttpResponse(html_template.render(context, request))
