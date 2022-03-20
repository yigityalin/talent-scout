from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.index, name='search'),
    path('results/<slug:by>/<slug:query>/page-<int:page>/save-all=<int:save_all>', views.results, name='results')
]