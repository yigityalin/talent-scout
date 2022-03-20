from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.index, name='search'),
    path('results/<slug:by>/<slug:query>', views.results, name='results')
]