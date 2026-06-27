from django.contrib import admin

from .models import CompteBancaire, TransactionBancaire


@admin.register(CompteBancaire)
class CompteBancaireAdmin(admin.ModelAdmin):
    list_display = ('numero_compte', 'nom_titulaire', 'type_compte', 'solde', 'actif')
    search_fields = ('numero_compte', 'nom_titulaire')
    list_filter = ('type_compte', 'actif')


@admin.register(TransactionBancaire)
class TransactionBancaireAdmin(admin.ModelAdmin):
    list_display = ('compte', 'type_transaction', 'montant', 'solde_avant', 'solde_apres', 'date_transaction')
    search_fields = ('compte__numero_compte', 'compte__nom_titulaire')
    list_filter = ('type_transaction', 'date_transaction')

# Register your models here.
