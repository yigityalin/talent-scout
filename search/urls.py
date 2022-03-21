from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.index, name='search'),
    path('results/user/<slug:login>', views.user_details, name='user'),
    path('results/<slug:by>/<slug:query>/page-<int:page>', views.results, name='results')
]