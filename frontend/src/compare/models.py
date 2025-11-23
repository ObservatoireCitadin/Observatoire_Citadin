from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Categorie(models.Model):
    titre = models.CharField(max_length=100)
    def __str__(self):
        return self.titre

class Critere(models.Model):
    titre = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    categorie = models.ForeignKey(Categorie, null=True, on_delete=models.PROTECT)
    estStandard = models.BooleanField(default=True)

    def __str__(self):
        return self.titre

class Ville(models.Model):
    nom = models.CharField(max_length=255, unique=True)
    url = models.CharField(max_length=255)
    criteres = models.ManyToManyField(Critere, related_name='Ville')
    description = models.TextField(null=True, blank=True)
    population = models.IntegerField(null=True, blank=True)
    departement = models.CharField(max_length=100, null=True, blank=True)
    prenomMaire = models.CharField(max_length=100, null=True, blank=True)
    nomMaire = models.CharField(max_length=100, null=True, blank=True)
    dateNaissanceMaire = models.DateField(null=True, blank=True)
    ageMaire = models.IntegerField(null=True, blank=True)
    sexMaire = models.CharField(max_length=1, null=True, blank=True)
    professionMaire = models.CharField(max_length=100, null=True, blank=True)
    ouverte = models.BooleanField(default=False)
    nbInscrits = models.IntegerField(null=True, blank=True)
    AbstentionPremierTour = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    votesBlancPremierTour = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    votesNulsPremierTour = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    codeCommune = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.nom

    # def __init__(self, *args, **kwargs):
    #     self.criteres.add(Critere.objects.filter(estStandard=True))

class Charte(models.Model):
    titre = models.CharField(max_length=100)
    lienPhoto = models.CharField(max_length=255, null=True, blank=True)
    photo = models.ImageField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    site = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.titre


class Liste(models.Model):
    nom = models.CharField(max_length=100, null=True, blank=True)
    slogan = models.CharField(max_length=250, null=True, blank=True)
    teteDeListe = models.CharField(max_length=100, null=True, blank=True)
    auteur = models.ManyToManyField(User, default=1)
    presentation = models.TextField(null=True, blank=True)
    ville = models.ForeignKey(Ville, on_delete=models.PROTECT)
    couleur = models.CharField(max_length=100, null=True)
    lienPhoto = models.CharField(max_length=255, null=True, blank=True)
    photo = models.ImageField(null=True, blank=True)
    site = models.CharField(max_length=200, null=True, blank=True)
    twitter = models.CharField(max_length=150, null=True, blank=True)
    validee = models.BooleanField(default=True)
    chartes = models.ManyToManyField(Charte, related_name='liste', blank=True)
    score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    scoreInscrit = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    scoreVoix = models.IntegerField(null=True, blank=True)
    secondTour = models.BooleanField(default=True)
    fusionAvec = models.ForeignKey("self", null=True, blank=True, on_delete=models.PROTECT)
    elu = models.BooleanField(default=False)

    class Meta:
        verbose_name = "liste"
        ordering = ['nom']

    def __str__(self):
        if self.nom is not None:
            result = self.nom
        elif self.couleur is not None:
            result = self.couleur
        else:
            result = self.ville.nom
        return result

class Promesse(models.Model):
    critere = models.ForeignKey(Critere, on_delete=models.PROTECT)
    titre = models.TextField()
    description = models.TextField(null=True, blank=True)
    liste = models.ForeignKey(Liste, on_delete=models.PROTECT)
    estUnePriorite = models.BooleanField(default=False)

    def __str__(self):
        return self.titre

class Contact(models.Model):
    email = models.EmailField(null=True, blank=True)
    traite = models.BooleanField(default=False)
    date = models.DateTimeField(default=datetime.now, blank=True)
    #ville = models.ForeignKey(Ville, on_delete=models.PROTECT, null=True, blank=True)
    ville = models.CharField(max_length=200 ,null=True, blank=True)
    liste = models.ForeignKey(Liste, on_delete=models.PROTECT, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    SOURCE_CHOICES = [
        ('ACC', 'Formulaire contact'),
        ('VSL', 'Ville sans liste'),
        ('VAL', 'Ville avec listes'),
        ('SIN', 'Singalement'),
        ('LST', 'Liste'),
    ]
    source = models.CharField(max_length=3, choices=SOURCE_CHOICES, default='ACC',)
    resteInforme = models.BooleanField(default=True)

    def __str__(self):
        return self.email
