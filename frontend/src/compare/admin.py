from django.contrib import admin
from .models import Liste, Ville, Critere, Promesse, Categorie, Contact, Charte
from django.contrib.auth.models import User


def addAdmin(modeladmin, request, queryset):
    for Liste in queryset:
        Liste.auteur.add(*User.objects.filter(is_superuser=True))
        Liste.save()

addAdmin.short_description = 'Ajouter les admins'


def addBertrand(modeladmin, request, queryset):
    for Liste in queryset:
        Liste.auteur.add(*User.objects.filter(username='Bertrand'))
        Liste.save()

addBertrand.short_description = 'Ajouter Bertrand auteur'


def validerListe(modeladmin, request, queryset):
    for liste in queryset:
        liste.validee=True
        liste.save()
validerListe.short_description = 'Valider listes'

def invaliderListe(modeladmin, request, queryset):
    for liste in queryset:
        liste.validee=False
        liste.save()
invaliderListe.short_description = 'Invalider listes'

def maintenu(modeladmin, request, queryset):
    for liste in queryset:
        liste.secondTour=True
        liste.save()
maintenu.short_description = 'Maintenir listes'

def nonMaintenu(modeladmin, request, queryset):
    for liste in queryset:
        liste.secondTour=False
        liste.save()
nonMaintenu.short_description = 'Ne pas maintenir listes'

def calculSecondTour(modeladmin, request, queryset):
    for liste in queryset :
        if liste.score is None :
            liste.secondTour = True
        else :
            if int(liste.score) < 10 :
                liste.secondTour = False
            else :
                liste.secondTour = True
        liste.save()
calculSecondTour.short_description = 'Calcul maintien second tour'

class ListeAdmin(admin.ModelAdmin):
    model = Liste
    list_display = ['__str__', 'nom', 'teteDeListe', 'couleur', 'score', 'secondTour', 'ville', 'get_auteurs', 'validee']
    search_fields = ['nom', 'couleur', 'teteDeListe', 'ville__nom']
    list_filter = ('validee',)
    actions = [addAdmin, validerListe,invaliderListe, addBertrand, calculSecondTour, maintenu, nonMaintenu]
    # fields = ('nom', 'teteDeListe', 'ville', 'couleur', 'lienPhoto','photo', 'presentation', 'slogan', 'site', 'auteur') #Réordonner ou Uniquement ces champs affichés dans le formulaire
    empty_value_display = '-------'
    filter_horizontal = ('auteur', 'chartes')
    list_display_links = ('__str__', 'nom', 'teteDeListe', 'couleur')
    autocomplete_fields = ['ville', 'fusionAvec']
    # list_select_related = ('ville',)
    save_on_top = True
    fieldsets = (
        (None, {
            'fields': (
                ('nom', 'teteDeListe', 'couleur'),('ville', 'lienPhoto', 'twitter'), ('score','secondTour','fusionAvec', 'elu'), 'chartes','photo', 'presentation', 'validee', 'slogan', 'site',
                'auteur')
        }),
        # ('Advanced options', {
        #     'classes': ('collapse',),
        #     'fields': ('registration_required', 'template_name'),
        # }),
    )

    def get_auteurs(self, obj):
        return ", ".join([a.username for a in obj.auteur.all()])

admin.site.register(Liste, ListeAdmin)

def ouvrir(modeladmin, request, queryset):
    for Ville in queryset:
        Ville.ouverte = True
        Ville.save()
ouvrir.short_description = 'Ouvrir'


def fermer(modeladmin, request, queryset):
    for Ville in queryset:
        Ville.ouverte = False
        Ville.save()
fermer.short_description = 'Fermer'


def ajouterCriteres(modeladmin, request, queryset):
    for Ville in queryset:
        Ville.criteres.add(*Critere.objects.filter(estStandard=True))
        Ville.save()
ajouterCriteres.short_description = 'Ajouter les critères standards sur les villes sélectionnées'

class VilleAdmin(admin.ModelAdmin):
    model = Ville
    list_display = ['nom', 'departement', 'population', 'ouverte']
    ordering = ('-ouverte', '-population',)
    search_fields = ['nom']
    filter_horizontal = ('criteres',)
    actions = [ouvrir, fermer, ajouterCriteres]


admin.site.register(Ville, VilleAdmin)
admin.site.register(Critere)


class PromesseAdmin(admin.ModelAdmin):
    model = Promesse
    list_display = ['id','titre','ville','liste', 'critere', 'estUnePriorite', 'get_auteurs']
    ordering = ('-id',)

    def ville(self, obj):
        return obj.liste.ville

    def get_auteurs(self, obj):
        return ", ".join([a.username for a in obj.liste.auteur.all()])

admin.site.register(Promesse, PromesseAdmin)

admin.site.register(Categorie)

class CharteAdmin(admin.ModelAdmin):
    model = Charte
    ordering = ('titre',)
admin.site.register(Charte, CharteAdmin)

def traite(modeladmin, request, queryset):
    for c in queryset:
        c.traite=True
        c.save()
traite.short_description = 'Contacts traités'

class ContactAdmin(admin.ModelAdmin):
    model = Contact
    list_display = ['email', 'date', 'source', 'ville', 'liste', 'traite']
    ordering = ('-date',)
    radio_fields = {"source": admin.VERTICAL}
    actions = [traite]
    autocomplete_fields = ['liste']
admin.site.register(Contact, ContactAdmin)
# Register your models here.
