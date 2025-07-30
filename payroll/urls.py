from django.urls import path
from . import views

urlpatterns = [
    path('mrf/', views.mrf_list, name='mrf_list'),
    path('mrf/create/', views.create_mrf, name='create_mrf'),
    path('mrf/edit/', views.edit_mrf, name='edit_mrf'),
    path('mrf/delete/', views.delete_mrf, name='delete_mrf'),
    path('mrf/get-details/', views.get_mrf_details, name='get_mrf_details'),
] 