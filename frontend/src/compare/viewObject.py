from compare.models import Promesse
from dal import autocomplete
from .models import Ville

class vPromesse:
    def __init__(self, l, p):
        self.liste = l
        self.promesse = p


class vCritere:
    def __init__(self, cri, ls):
        self.titre = cri.titre
        self.listes = ls
        for l in self.listes:
            ps = Promesse.objects.filter(liste=l,critere=cri)
            c=False
            for p in ps:
                if p.critere == cri:
                    self.promesses.append(vPromesse(l, p))
                    c=True
            if c==False:
                self.promesses.append(vPromesse(l, None)) #Si pas de critère pour cette liste

class vCategorie:
    def __init__(self, cat, v, ls):
        self.titre = cat.titre
        self.criteres = []
        for cri in v.criteres.all():
            if cri.categorie==cat:
                self.criteres.append(vCritere(cri, ls))



class VilleAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !

        qs = Ville.objects.all().order_by('ouverte','-nom').reverse()

        if self.q:
            qs = qs.filter(nom__icontains=self.q)

        return qs
