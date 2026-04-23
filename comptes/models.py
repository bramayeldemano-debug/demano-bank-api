from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class CompteBancaire(models.Model):
    TYPE_COMPTE_CHOICES = [
        ('COURANT', 'Compte Courant'),
        ('EPARGNE', 'Compte Épargne'),
        ('TERME', 'Compte à Terme'),
    ]

    numero_compte = models.CharField(
        max_length=20,
        unique=True,
        help_text="Numéro unique du compte bancaire"
    )
    nom_titulaire = models.CharField(
        max_length=100,
        help_text="Nom complet du titulaire du compte"
    )
    type_compte = models.CharField(
        max_length=10,
        choices=TYPE_COMPTE_CHOICES,
        default='COURANT',
        help_text="Type de compte bancaire"
    )
    solde = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Solde actuel du compte en unité monétaire"
    )
    date_ouverture = models.DateTimeField(
        auto_now_add=True,
        help_text="Date et heure d'ouverture du compte"
    )
    date_modification = models.DateTimeField(
        auto_now=True,
        help_text="Dernière date de modification du compte"
    )
    actif = models.BooleanField(
        default=True,
        help_text="Statut d'activation du compte"
    )

    class Meta:
        verbose_name = "Compte Bancaire"
        verbose_name_plural = "Comptes Bancaires"
        ordering = ['-date_ouverture']

    def __str__(self):
        return f"{self.numero_compte} - {self.nom_titulaire}"


class TransactionBancaire(models.Model):
    TYPE_TRANSACTION_CHOICES = [
        ('DEPOT', 'Dépôt'),
        ('RETRAIT', 'Retrait'),
    ]

    compte = models.ForeignKey(
        CompteBancaire,
        on_delete=models.CASCADE,
        related_name='transactions',
        help_text="Compte concerné par la transaction"
    )
    type_transaction = models.CharField(
        max_length=10,
        choices=TYPE_TRANSACTION_CHOICES,
        help_text="Type de transaction bancaire"
    )
    montant = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1.00'))],
        help_text="Montant positif de la transaction"
    )
    solde_avant = models.DecimalField(max_digits=15, decimal_places=2)
    solde_apres = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255, blank=True, default='')
    date_transaction = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transaction Bancaire"
        verbose_name_plural = "Transactions Bancaires"
        ordering = ['-date_transaction']

    def __str__(self):
        return f"{self.type_transaction} {self.montant} - {self.compte.numero_compte}"
