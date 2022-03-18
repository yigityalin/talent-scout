from django.core.mail import BadHeaderError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import loader
from .utils.github_ import GitHub
from .models import Search
from .forms import SearchForm


def index(request):
    form = SearchForm(request.POST or None)
    context = {
        "form": form,
        "form_received": False,
    }
    if form.is_valid():
        obj = form.save()
        try:
            context["form_received"] = True
            context["message"] = "I received your message. Thank you."
        except BadHeaderError:
            context["form_received"] = False
            context["message"] = "Invalid header found."
        except Exception:
            context["message"] = "I cannot receive your message right now. Please use the links above."
        finally:
            return redirect(request.path)
    html_template = loader.get_template('search/search.html')
    return HttpResponse(html_template.render(context, request))
