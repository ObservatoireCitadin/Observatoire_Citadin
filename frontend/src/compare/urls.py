from django.contrib import admin
from django.urls import path, re_path
from . import views
from dal import autocomplete
from . import models
from .viewObject import VilleAutocomplete
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('liste/<int:id>', views.liste, name='liste'),
    path('test', views.test, name='test'),
    path('compare/<str:nom>', views.compare, name='compare'),
    re_path('ville-autocomplete/$', VilleAutocomplete.as_view(model=models.Ville), name='ville-autocomplete'),
    path('revendiquer-ma-liste', views.revendiquer, name='revendiquer'),
    path('<str:url>', views.ville, name='ville'),
    path('iframe/liste/<int:id>', views.listeIframe, name='listeView'),
    path('iframe/<str:url>', views.compareIframe, name='compareView'),
]
