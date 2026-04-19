from django.urls import path
from . import views

urlpatterns = [
    path('comptes/', views.liste_comptes, name='liste_comptes'),
    path('comptes/creer/', views.creer_compte, name='creer_compte'),
    path('comptes/<int:pk>/', views.detail_compte, name='detail_compte'),
    path('comptes/<int:pk>/modifier/', views.modifier_compte, name='modifier_compte'),
    path('comptes/<int:pk>/supprimer/', views.supprimer_compte, name='supprimer_compte'),
]