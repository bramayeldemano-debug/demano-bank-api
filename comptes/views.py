from django.db import transaction as db_transaction
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import CompteBancaire, TransactionBancaire
from .serializers import (
    CasTestsManuelsResponseSerializer,
    CompteBancaireCreateSerializer,
    CompteBancaireSerializer,
    CompteBancaireUpdateSerializer,
    HistoriqueTransactionsResponseSerializer,
    OperationBancaireSerializer,
    OperationBancaireResponseSerializer,
    TransactionBancaireSerializer,
)


def get_compte(pk):
    try:
        return CompteBancaire.objects.get(pk=pk)
    except CompteBancaire.DoesNotExist:
        return None


@extend_schema(
    tags=['Comptes Bancaires'],
    summary="Lister les comptes bancaires",
    responses={200: CompteBancaireSerializer(many=True)},
    description="Récupère la liste de tous les comptes bancaires actifs.",
)
@api_view(['GET'])
def liste_comptes(request):
    comptes = CompteBancaire.objects.filter(actif=True)
    serializer = CompteBancaireSerializer(comptes, many=True)
    return Response(serializer.data)


@extend_schema(
    tags=['Comptes Bancaires'],
    summary="Consulter un compte bancaire",
    responses={200: CompteBancaireSerializer, 404: None},
    description="Récupère les détails d'un compte bancaire par son ID.",
)
@api_view(['GET'])
def detail_compte(request, pk):
    compte = get_compte(pk)
    if compte is None:
        return Response({'erreur': 'Compte bancaire non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CompteBancaireSerializer(compte)
    return Response(serializer.data)


@extend_schema(
    tags=['Comptes Bancaires'],
    summary="Créer un compte bancaire",
    request=CompteBancaireCreateSerializer,
    responses={201: CompteBancaireSerializer, 400: None},
    description="Crée un nouveau compte bancaire et enregistre le dépôt initial si le solde est positif.",
    examples=[
        OpenApiExample(
            'Création de compte',
            value={
                'numero_compte': 'ACC000001',
                'nom_titulaire': 'DEMANO BRAMAEL',
                'type_compte': 'COURANT',
                'solde': '10000.00',
            },
            request_only=True,
        )
    ],
)
@api_view(['POST'])
def creer_compte(request):
    serializer = CompteBancaireCreateSerializer(data=request.data)
    if serializer.is_valid():
        compte = serializer.save()
        response_serializer = CompteBancaireSerializer(compte)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Comptes Bancaires'],
    summary="Modifier un compte bancaire",
    request=CompteBancaireUpdateSerializer,
    responses={200: CompteBancaireSerializer, 400: None, 404: None},
    description="Met à jour les informations d'un compte bancaire.",
)
@api_view(['PUT'])
def modifier_compte(request, pk):
    compte = get_compte(pk)
    if compte is None:
        return Response({'erreur': 'Compte bancaire non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CompteBancaireUpdateSerializer(compte, data=request.data, partial=True)
    if serializer.is_valid():
        compte_modifie = serializer.save()
        response_serializer = CompteBancaireSerializer(compte_modifie)
        return Response(response_serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Comptes Bancaires'],
    summary="Supprimer logiquement un compte bancaire",
    responses={204: None, 404: None},
    description="Supprime un compte bancaire par désactivation logique.",
)
@api_view(['DELETE'])
def supprimer_compte(request, pk):
    compte = get_compte(pk)
    if compte is None:
        return Response({'erreur': 'Compte bancaire non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    compte.actif = False
    compte.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=['Transactions Bancaires'],
    summary="Effectuer un dépôt",
    request=OperationBancaireSerializer,
    responses={200: OperationBancaireResponseSerializer, 400: None, 404: None},
    description="Ajoute un montant positif au solde du compte et enregistre la transaction.",
    examples=[
        OpenApiExample(
            'Dépôt valide',
            value={'montant': '5000.00', 'description': 'Dépôt agence'},
            request_only=True,
        )
    ],
)
@api_view(['POST'])
def effectuer_depot(request, pk):
    compte = get_compte(pk)
    if compte is None:
        return Response({'erreur': 'Compte bancaire non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    if not compte.actif:
        return Response({'erreur': 'Compte inactif'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = OperationBancaireSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    montant = serializer.validated_data['montant']
    description = serializer.validated_data.get('description') or 'Dépôt'

    with db_transaction.atomic():
        solde_avant = compte.solde
        compte.solde += montant
        compte.save()
        transaction = TransactionBancaire.objects.create(
            compte=compte,
            type_transaction='DEPOT',
            montant=montant,
            solde_avant=solde_avant,
            solde_apres=compte.solde,
            description=description,
        )

    return Response({
        'message': 'Dépôt effectué avec succès',
        'solde_actuel': str(compte.solde),
        'transaction': TransactionBancaireSerializer(transaction).data,
    }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Transactions Bancaires'],
    summary="Effectuer un retrait",
    request=OperationBancaireSerializer,
    responses={
        200: OperationBancaireResponseSerializer,
        400: OpenApiResponse(description='Montant invalide, solde insuffisant ou compte inactif'),
        404: OpenApiResponse(description='Compte bancaire non trouvé'),
    },
    description="Retire un montant du compte si le solde disponible est suffisant.",
    examples=[
        OpenApiExample(
            'Retrait valide',
            value={'montant': '2000.00', 'description': 'Retrait guichet'},
            request_only=True,
        )
    ],
)
@api_view(['POST'])
def effectuer_retrait(request, pk):
    compte = get_compte(pk)
    if compte is None:
        return Response({'erreur': 'Compte bancaire non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    if not compte.actif:
        return Response({'erreur': 'Compte inactif'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = OperationBancaireSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    montant = serializer.validated_data['montant']
    description = serializer.validated_data.get('description') or 'Retrait'

    if compte.solde < montant:
        return Response({
            'erreur': 'Solde insuffisant',
            'solde_disponible': str(compte.solde),
            'montant_demande': str(montant),
        }, status=status.HTTP_400_BAD_REQUEST)

    with db_transaction.atomic():
        solde_avant = compte.solde
        compte.solde -= montant
        compte.save()
        transaction = TransactionBancaire.objects.create(
            compte=compte,
            type_transaction='RETRAIT',
            montant=montant,
            solde_avant=solde_avant,
            solde_apres=compte.solde,
            description=description,
        )

    return Response({
        'message': 'Retrait effectué avec succès',
        'solde_actuel': str(compte.solde),
        'transaction': TransactionBancaireSerializer(transaction).data,
    }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Transactions Bancaires'],
    summary="Lister les transactions d'un compte",
    responses={200: HistoriqueTransactionsResponseSerializer, 404: None},
    description="Retourne l'historique des dépôts et retraits d'un compte.",
)
@api_view(['GET'])
def historique_transactions(request, pk):
    compte = get_compte(pk)
    if compte is None:
        return Response({'erreur': 'Compte bancaire non trouvé'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TransactionBancaireSerializer(compte.transactions.all(), many=True)
    return Response({
        'compte': compte.numero_compte,
        'solde_actuel': str(compte.solde),
        'transactions': serializer.data,
    }, status=status.HTTP_200_OK)


CAS_TESTS_MANUELS = [
    {
        'fonction': 'Créer un compte',
        'objectif': 'Vérifier que le système crée un compte bancaire valide.',
        'preconditions': 'Aucun compte avec le même numéro ne doit exister.',
        'donnees_test': {
            'numero_compte': 'ACC000001',
            'nom_titulaire': 'DEMANO BRAMAEL',
            'type_compte': 'COURANT',
            'solde': '10000.00',
        },
        'resultat_attendu': 'Code 201, compte créé et transaction de dépôt initial enregistrée.',
        'endpoint': '/api/comptes/creer/',
        'methode': 'POST',
    },
    {
        'fonction': 'Lister les comptes',
        'objectif': 'Vérifier que le système retourne les comptes actifs.',
        'preconditions': 'Au moins un compte actif existe.',
        'donnees_test': {},
        'resultat_attendu': 'Code 200 avec un tableau contenant les comptes actifs.',
        'endpoint': '/api/comptes/',
        'methode': 'GET',
    },
    {
        'fonction': 'Consulter un compte',
        'objectif': 'Vérifier que le détail d’un compte est accessible par son identifiant.',
        'preconditions': 'Un compte avec cet identifiant existe.',
        'donnees_test': {'id': 1},
        'resultat_attendu': 'Code 200 avec les informations du compte et ses transactions.',
        'endpoint': '/api/comptes/{id}/',
        'methode': 'GET',
    },
    {
        'fonction': 'Effectuer un dépôt',
        'objectif': 'Vérifier que le solde augmente après un dépôt valide.',
        'preconditions': 'Le compte existe et est actif.',
        'donnees_test': {'montant': '5000.00', 'description': 'Dépôt agence'},
        'resultat_attendu': 'Code 200, solde augmenté et transaction DEPOT enregistrée.',
        'endpoint': '/api/comptes/{id}/depot/',
        'methode': 'POST',
    },
    {
        'fonction': 'Effectuer un retrait',
        'objectif': 'Vérifier que le système retire l’argent si le solde est suffisant.',
        'preconditions': 'Le compte existe, est actif et possède un solde suffisant.',
        'donnees_test': {'montant': '2000.00', 'description': 'Retrait guichet'},
        'resultat_attendu': 'Code 200, solde diminué et transaction RETRAIT enregistrée.',
        'endpoint': '/api/comptes/{id}/retrait/',
        'methode': 'POST',
    },
]


@extend_schema(
    tags=['Tests Manuels'],
    summary="Afficher les cas de test manuels",
    responses={200: CasTestsManuelsResponseSerializer},
    description="Retourne les différents cas de test manuel des 5 fonctions principales du système.",
)
@api_view(['GET'])
def cas_tests_manuels(request):
    return Response({
        'total': len(CAS_TESTS_MANUELS),
        'cas_tests': CAS_TESTS_MANUELS,
    }, status=status.HTTP_200_OK)
