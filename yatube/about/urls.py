"""Module with urls of About app."""

from django.urls import path

from yatube.about import views

app_name = 'about'

urlpatterns = [
    path('author/', views.AboutAuthorView.as_view(), name='author'),
    path('tech/', views.AboutTechView.as_view(), name='tech'),
]
