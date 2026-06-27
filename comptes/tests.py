<<<<<<< HEAD
WXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX+
XXfrom decimal import Decimal
=======
from decimal import Decimal
>>>>>>> 1520cf0980d6dc46dbdfe1a5f1d7d9354128ba8c

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CompteBancaire, TransactionBancaire


class FonctionsBancairesTests(APITestCase):
<<<<<<< HEAD
=======
    def test_accueil(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

>>>>>>> 1520cf0980d6dc46dbdfe1a5f1d7d9354128ba8c
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

<<<<<<< HEAD
=======
    def test_creer_compte_invalide(self):
        response = self.client.post(reverse('creer_compte'), {
            'numero_compte': 'ACC1',
            'nom_titulaire': 'A',
            'type_compte': 'COURANT',
            'solde': '10000.00',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('numero_compte', response.data)
        self.assertIn('nom_titulaire', response.data)

>>>>>>> 1520cf0980d6dc46dbdfe1a5f1d7d9354128ba8c
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

    def test_modifier_compte(self):
        compte = CompteBancaire.objects.create(numero_compte='ACC000003B', nom_titulaire='Client Test', solde=1000)

        response = self.client.put(reverse('modifier_compte', args=[compte.id]), {
            'nom_titulaire': 'Client Modifie',
            'type_compte': 'EPARGNE',
            'solde': '1200.00',
        }, format='json')
        compte.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(compte.nom_titulaire, 'Client Modifie')
        self.assertEqual(compte.type_compte, 'EPARGNE')
        self.assertEqual(compte.solde, Decimal('1200.00'))

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
<<<<<<< HEAD
=======

    def test_retrait_compte_inactif(self):
        compte = CompteBancaire.objects.create(
            numero_compte='ACC000006B',
            nom_titulaire='Client Test',
            solde=1000,
            actif=False,
        )

        response = self.client.post(reverse('effectuer_retrait', args=[compte.id]), {
            'montant': '100.00',
            'description': 'Retrait refuse',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['erreur'], 'Compte inactif')

    def test_historique_transactions(self):
        compte = CompteBancaire.objects.create(numero_compte='ACC000007', nom_titulaire='Client Test', solde=1000)
        TransactionBancaire.objects.create(
            compte=compte,
            type_transaction='DEPOT',
            montant=Decimal('300.00'),
            solde_avant=Decimal('700.00'),
            solde_apres=Decimal('1000.00'),
            description='Depot test',
        )

        response = self.client.get(reverse('historique_transactions', args=[compte.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['compte'], 'ACC000007')
        self.assertEqual(len(response.data['transactions']), 1)

    def test_supprimer_compte(self):
        compte = CompteBancaire.objects.create(numero_compte='ACC000008', nom_titulaire='Client Test', solde=1000)

        response = self.client.delete(reverse('supprimer_compte', args=[compte.id]))
        compte.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(compte.actif)

    def test_depot_compte_inactif(self):
        compte = CompteBancaire.objects.create(
            numero_compte='ACC000009',
            nom_titulaire='Client Test',
            solde=1000,
            actif=False,
        )

        response = self.client.post(reverse('effectuer_depot', args=[compte.id]), {
            'montant': '300.00',
            'description': 'Depot refuse',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['erreur'], 'Compte inactif')

    def test_consulter_compte_inexistant(self):
        response = self.client.get(reverse('detail_compte', args=[999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cas_tests_manuels(self):
        response = self.client.get(reverse('cas_tests_manuels'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 5)
>>>>>>> 1520cf0980d6dc46dbdfe1a5f1d7d9354128ba8c
