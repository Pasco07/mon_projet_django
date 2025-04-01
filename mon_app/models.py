from django.db import models

class Pays(models.Model):
    UEMOA_COUNTRIES = [
    ('BJ', 'Bénin'),
    ('BF', 'Burkina Faso'),
    ('CI', 'Côte d\'Ivoire'),
    ('GW', 'Guinée-Bissau'),
    ('ML', 'Mali'),
    ('NE', 'Niger'),
    ('SN', 'Sénégal'),
    ('TG', 'Togo'),
]
    nom = models.CharField(max_length=100, choices = UEMOA_COUNTRIES)

    def __str__(self):
        return self.get_nom_display()

class Titre(models.Model):
    TYPE_CHOICES = [
        ('BAT', 'BAT'),
        ('OAT', 'OAT'),
    ]
    TYPE_AMORTIS =[
            ('IN FINE','In fine'),
            ('LINEAIRE','Linéaire'),
            ('DIFFERE','Differe'),
    ]
    pays = models.ForeignKey(Pays, on_delete=models.CASCADE, related_name='titres')
    type_titre = models.CharField(max_length=3, choices=TYPE_CHOICES)
    isin = models.CharField(max_length=12, unique=True)
    denomination = models.CharField(max_length=200)
    adjudication = models.CharField(max_length=50)
    duree = models.CharField(max_length=50)
    date_valeur = models.DateField()
    valeur_nominale = models.DecimalField(max_digits=15, decimal_places=2)
    taux_interet = models.DecimalField(max_digits=5, decimal_places=2)
    taux_coupon_couru = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    type_amortissement = models.CharField( max_length=10, choices=TYPE_AMORTIS, default='INFINE')
    annees_differe = models.PositiveIntegerField(default=0)
    prix_pondere = models.DecimalField(max_digits=15,decimal_places=2,null=True,blank=True)

    def __str__(self):
        return f"{self.isin} - {self.denomination}"

