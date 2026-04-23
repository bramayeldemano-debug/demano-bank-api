from decimal import Decimal

from rest_framework import serializers

from .models import CompteBancaire, TransactionBancaire


class TransactionBancaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionBancaire
        fields = [
            'id',
            'type_transaction',
            'montant',
            'solde_avant',
            'solde_apres',
            'description',
            'date_transaction',
        ]
        read_only_fields = fields


class CompteBancaireSerializer(serializers.ModelSerializer):
    transactions = TransactionBancaireSerializer(many=True, read_only=True)

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
            'actif',
            'transactions',
        ]
        read_only_fields = ['id', 'date_ouverture', 'date_modification', 'transactions']

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
            'solde',
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

    def create(self, validated_data):
        compte = CompteBancaire.objects.create(**validated_data)

        if compte.solde > Decimal('0.00'):
            TransactionBancaire.objects.create(
                compte=compte,
                type_transaction='DEPOT',
                montant=compte.solde,
                solde_avant=Decimal('0.00'),
                solde_apres=compte.solde,
                description='Solde initial à la création du compte',
            )

        return compte


class CompteBancaireUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompteBancaire
        fields = [
            'nom_titulaire',
            'type_compte',
            'solde',
            'actif',
        ]

    def validate_nom_titulaire(self, value):
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Le nom du titulaire doit contenir au moins 2 caractères."
            )
        return value.strip() if value else value


class OperationBancaireSerializer(serializers.Serializer):
    montant = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('1.00'))
    description = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')


class OperationBancaireResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    solde_actuel = serializers.CharField()
    transaction = TransactionBancaireSerializer()


class HistoriqueTransactionsResponseSerializer(serializers.Serializer):
    compte = serializers.CharField()
    solde_actuel = serializers.CharField()
    transactions = TransactionBancaireSerializer(many=True)


class CasTestManuelSerializer(serializers.Serializer):
    fonction = serializers.CharField()
    objectif = serializers.CharField()
    preconditions = serializers.CharField()
    donnees_test = serializers.DictField()
    resultat_attendu = serializers.CharField()
    endpoint = serializers.CharField()
    methode = serializers.CharField()


class CasTestsManuelsResponseSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    cas_tests = CasTestManuelSerializer(many=True)
