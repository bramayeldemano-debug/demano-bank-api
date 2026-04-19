from rest_framework import serializers
from .models import CompteBancaire


class CompteBancaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompteBancaire
        fields = [
            'id',
            'numero_compte',
            'nom_titulaire',
            'type_compte',
            'solde',
            'date_ouverture',
            'date_modification',
            'actif'
        ]
        read_only_fields = ['id', 'date_ouverture', 'date_modification']

    def validate_numero_compte(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Le numéro de compte doit contenir au moins 8 caractères."
            )
        return value

    def validate_nom_titulaire(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Le nom du titulaire doit contenir au moins 2 caractères."
            )
        return value.strip()


class CompteBancaireCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompteBancaire
        fields = [
            'numero_compte',
            'nom_titulaire',
            'type_compte',
            'solde'
        ]

    def validate_numero_compte(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Le numéro de compte doit contenir au moins 8 caractères."
            )
        return value

    def validate_nom_titulaire(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Le nom du titulaire doit contenir au moins 2 caractères."
            )
        return value.strip()


class CompteBancaireUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompteBancaire
        fields = [
            'nom_titulaire',
            'type_compte',
            'solde',
            'actif'
        ]

    def validate_nom_titulaire(self, value):
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Le nom du titulaire doit contenir au moins 2 caractères."
            )
        return value.strip() if value else value