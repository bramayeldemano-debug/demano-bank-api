from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CompteBancaire, TransactionBancaire


class FonctionsBancairesTests(APITestCase):
    def test_creer_compte(self):
        response = self.client.post(reverse('creer_compte'), {
            'numero_compte': 'ACC000001',
            'nom_titulaire': 'DEMANO BRAMAEL',
            'type_compte': 'COURANT',
            'solde': '10000.00',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CompteBancaire.objects.count(), 1)
        self.assertEqual(TransactionBancaire.objects.count(), 1)

    def test_lister_comptes(self):
        CompteBancaire.objects.create(numero_compte='ACC000002', nom_titulaire='Client Test', solde=1000)

        response = self.client.get(reverse('liste_comptes'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_consulter_compte(self):
        compte = CompteBancaire.objects.create(numero_compte='ACC000003', nom_titulaire='Client Test', solde=1000)

        response = self.client.get(reverse('detail_compte', args=[compte.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['numero_compte'], 'ACC000003')

    def test_effectuer_depot(self):
        compte = CompteBancaire.objects.create(numero_compte='ACC000004', nom_titulaire='Client Test', solde=1000)

        response = self.client.post(reverse('effectuer_depot', args=[compte.id]), {
            'montant': '500.00',
            'description': 'Dépôt test',
        }, format='json')
        compte.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(compte.solde, Decimal('1500.00'))
        self.assertEqual(compte.transactions.filter(type_transaction='DEPOT').count(), 1)

    def test_effectuer_retrait(self):
        compte = CompteBancaire.objects.create(numero_compte='ACC000005', nom_titulaire='Client Test', solde=1000)

        response = self.client.post(reverse('effectuer_retrait', args=[compte.id]), {
            'montant': '400.00',
            'description': 'Retrait test',
        }, format='json')
        compte.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(compte.solde, Decimal('600.00'))
        self.assertEqual(compte.transactions.filter(type_transaction='RETRAIT').count(), 1)

    def test_retrait_solde_insuffisant(self):
        compte = CompteBancaire.objects.create(numero_compte='ACC000006', nom_titulaire='Client Test', solde=100)

        response = self.client.post(reverse('effectuer_retrait', args=[compte.id]), {
            'montant': '400.00',
            'description': 'Retrait impossible',
        }, format='json')
        compte.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(compte.solde, Decimal('100.00'))
