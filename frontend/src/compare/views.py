from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from compare.models import Liste, Promesse, Ville, Categorie, Contact, Critere
from compare.form import RechercheVille, FormContact, FormInfo, FormContactBlack
from compare.viewObject import vCategorie
from datetime import datetime
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Q

def listeIframe(request, id):
    return liste(request,id, iframe=False)

def liste(request, id, **kwargs):
    iframe = kwargs.get('iframe', True)
    formR = FormInfo(request.POST or None)
    formS = FormContactBlack(request.POST or None)
    l = get_object_or_404(Liste, id=id)
    ps = Promesse.objects.filter(liste_id=id)
    cats = Categorie.objects.all()
    prio = Promesse.objects.filter(liste_id=id, estUnePriorite=True)
    user = request.user
    modif=False
    if user in l.auteur.all() :
        modif=True
    if formS.is_valid() and 'signaler' in request.POST :
        email = formS.cleaned_data['email']
        comment = formS.cleaned_data['comment']
        inform = formS.cleaned_data['inform']
        c = Contact(email=email, comment=comment, source='SIN', resteInforme=inform, ville=l.ville, liste=l)
        c.save()
        modalSignal = True
    if formR.is_valid() and 'formR' in request.POST :
        email = formR.cleaned_data['email']
        c = Contact(email=email, ville=l.ville, source='LST', liste=l)
        c.save()
        modalFollow = True
    return render(request, 'compare/liste.html', locals())

def ville(request, url, **kwargs):
    formI = FormInfo(request.POST or None)
    formR = FormInfo(request.POST or None)
    formS = FormContactBlack(request.POST or None)
    v = Ville.objects.filter(url=url).first()
    if v is None : return erreur(request)
    #form.fields['Listes'].queryset = [l.pk for l in Liste.objects.filter(ville=v)]
    user = request.user
    secondTour = False
    elu = False
    if len(Liste.objects.filter(ville=v, elu=True))>0 : elu=True
    elif len(Liste.objects.filter(ville=v, score__isnull=False))>0 : secondTour=True

    if elu :
        ls = Liste.objects.filter(ville=v, elu=True).order_by('-score')
        lsnm = Liste.objects.filter(ville=v, elu=False).order_by('-score')
    else :
        ls = Liste.objects.filter(ville=v, secondTour=True).order_by('-score')
        lsnm = Liste.objects.filter(ville=v, secondTour=False).order_by('-score')

    #Process validation liste
    #if request.user.is_authenticated :
    #     ls = Liste.objects.filter(ville=v).order_by('?')
    # else :
    #     ls = Liste.objects.filter(ville=v, validee=True).order_by('?')

    iframe = kwargs.get('iframe', True)
    modal = False
    for l in ls:
        l.prio = Promesse.objects.filter(liste=l, estUnePriorite=True)
        l.estRejoint = Liste.objects.filter(fusionAvec=l);
        if user in l.auteur.all():
            l.modif = True
    if formS.is_valid() and 'signaler' in request.POST :
        email = formS.cleaned_data['email']
        comment = formS.cleaned_data['comment']
        inform = formS.cleaned_data['inform']
        villeContact = get_object_or_404(Ville, url=url)
        c = Contact(email=email, comment=comment, source='SIN', resteInforme=inform, ville=villeContact)
        c.save()
        modalSignal = True
    if formI.is_valid() and 'formI' in request.POST :
        email = formI.cleaned_data['email']
        villeContact = get_object_or_404(Ville, url=url)
        c = Contact(email=email, ville=villeContact, source='VSL')
        c.save()
        return accueil(request, modal=True)
    if formR.is_valid() and 'formR' in request.POST : #Formulaire rester informé depuis ville avec listes
        email = formI.cleaned_data['email']
        villeContact = get_object_or_404(Ville, url=url)
        c = Contact(email=email, ville=villeContact, source='VAL')
        c.save()
        modalFollow = True
    if 'formC' in request.POST :
        listes=request.POST.getlist('Listes',default=None)
        return compare(request, url, listes=listes)
    return render(request, 'compare/ville.html', locals())

def compareIframe(request, url):
    return compare(request,url, iframe=False)

def compare(request, url, **kwargs):
    vcats = []
    cats = Categorie.objects.all()
    v = get_object_or_404(Ville, url=url)
    ids = kwargs.get('listes', None)
    iframe = kwargs.get('iframe', True)
    ls=[]
    if ids is None :
        ls = Liste.objects.filter(ville=v, validee=True, secondTour=True).order_by('?')
    elif len(ids)>0 :
        ls = Liste.objects.filter(id__in = ids).order_by('?')
    else:
        ls = Liste.objects.filter(ville=v, validee=True, secondTour=True).order_by('?')
    for l in ls:
        l.prio=[]
        l.prio.extend(Promesse.objects.filter(liste=l, estUnePriorite=True))
        l.estRejoint = Liste.objects.filter(fusionAvec=l)
    for cat in cats:
        cat.cs = Critere.objects.filter(categorie=cat,Ville=v)
        for c in cat.cs:
            c.listes=[]
            for li in ls:
                l=Liste.objects.get(id=li.id)
                l.ps=Promesse.objects.filter(liste=li,critere=c)
                c.listes.append(l)

    for cat in cats:
        print(cat.cs)
        for c in cat.cs:
            print(c.listes)
            for l in c.listes:
                print(l.ps)
    return render(request, 'compare/compare.html', locals())

def accueil(request, **kwargs):
    formV = RechercheVille(request.POST or None)
    formC = FormContact(request.POST or None)
    cs = Categorie.objects.all()

    vs = Ville.objects.filter(ouverte=True).order_by('?')
    best = []
    for v in vs:
        v.nbL = len(Liste.objects.filter(ville=v, secondTour=True))
        v.prop = len(Promesse.objects.filter(liste__in = Liste.objects.filter(ville=v)))
        if v.prop>10:
            best.append(v)
        if len(best)>=4 : break
    #verif = (datetime.strptime("08/02/2020", "%d/%m/%Y") - datetime.now()).days
    #premier = (datetime.strptime("16/03/2020", "%d/%m/%Y") - datetime.now()).days
    for c in cs:
        c.criteres = []
        c.criteres.extend(Critere.objects.filter(categorie=c, estStandard=True))
    modal = kwargs.get('modal', False)
    if formV.is_valid():
        nom = formV.cleaned_data['ville']
        v = get_object_or_404(Ville, nom=nom)
        return redirect(ville, v.url)
    if formC.is_valid() and 'contact' in request.POST :
        email = formC.cleaned_data['email']
        comment = formC.cleaned_data['comment']
        inform = formC.cleaned_data['inform']
        c = Contact(email=email, comment=comment, source='ACC', resteInforme=inform)
        c.save()
        modal = True
    return render(request, 'compare/accueil.html', locals())

def test(request):
    return render(request, 'compare/test.html', locals())

def erreur(request):
    return render(request, 'compare/villeNotFound.html', locals())

def revendiquer(request):
    return redirect('https://framaforms.org/programmes-municipalesfr-1592861246')
