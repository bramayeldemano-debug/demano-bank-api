from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import CompteBancaire
from .serializers import (
    CompteBancaireSerializer,
    CompteBancaireCreateSerializer,
    CompteBancaireUpdateSerializer
)


@extend_schema(
    tags=['Comptes Bancaires'],
    responses={200: CompteBancaireSerializer(many=True)},
    description="Récupère la liste de tous les comptes bancaires actifs"
)
@api_view(['GET'])
def liste_comptes(request):
    comptes = CompteBancaire.objects.filter(actif=True)
    serializer = CompteBancaireSerializer(comptes, many=True)
    return Response(serializer.data)


@extend_schema(
    tags=['Comptes Bancaires'],
    responses={200: CompteBancaireSerializer, 404: None},
    description="Récupère les détails d'un compte bancaire par son ID"
)
@api_view(['GET'])
def detail_compte(request, pk):
    try:
        compte = CompteBancaire.objects.get(pk=pk)
    except CompteBancaire.DoesNotExist:
        return Response(
            {'erreur': 'Compte bancaire non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = CompteBancaireSerializer(compte)
    return Response(serializer.data)


@extend_schema(
    tags=['Comptes Bancaires'],
    request=CompteBancaireCreateSerializer,
    responses={201: CompteBancaireSerializer, 400: None},
    description="Crée un nouveau compte bancaire"
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
    request=CompteBancaireUpdateSerializer,
    responses={200: CompteBancaireSerializer, 400: None, 404: None},
    description="Met à jour les informations d'un compte bancaire"
)
@api_view(['PUT'])
def modifier_compte(request, pk):
    try:
        compte = CompteBancaire.objects.get(pk=pk)
    except CompteBancaire.DoesNotExist:
        return Response(
            {'erreur': 'Compte bancaire non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = CompteBancaireUpdateSerializer(compte, data=request.data, partial=True)
    if serializer.is_valid():
        compte_modifie = serializer.save()
        response_serializer = CompteBancaireSerializer(compte_modifie)
        return Response(response_serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Comptes Bancaires'],
    responses={204: None, 404: None},
    description="Supprime un compte bancaire (suppression logique)"
)
@api_view(['DELETE'])
def supprimer_compte(request, pk):
    try:
        compte = CompteBancaire.objects.get(pk=pk)
    except CompteBancaire.DoesNotExist:
        return Response(
            {'erreur': 'Compte bancaire non trouvé'},
            status=status.HTTP_404_NOT_FOUND
        )

    compte.actif = False
    compte.save()
    return Response(status=status.HTTP_204_NO_CONTENT)
