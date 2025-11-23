from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ListForm, CustomUserCreationForm, LoginForm
from django.contrib.auth.decorators import login_required
from compare.views import liste, accueil
from compare.models import Liste, Ville, Critere, Categorie, Promesse
from django.contrib.auth.decorators import login_required
from django.contrib import auth

# New registration form created from scratch
def connect(request):
    if request.method == 'POST':
        formIns = CustomUserCreationForm(request.POST or None)
        formCon = LoginForm(request.POST or None)

        if formIns.is_valid() and 'formIns' in request.POST:
            formIns.save()
            username = formIns.cleaned_data.get('username')
            password = formIns.cleaned_data.get('password2')
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect('/')

        if formCon.is_valid() and 'formCon' in request.POST:
            username = formCon.cleaned_data.get('username')
            password = formCon.cleaned_data.get('password')
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                # correct username and password login the user
                auth.login(request, user)
                return redirect('/')
            else:
                messages.error(request, 'Error wrong username/password')
    else:
        formIns = CustomUserCreationForm()
        formCon = LoginForm()

    return render(request, 'users/connect.html', {'formCon': formCon, 'formIns': formIns})

@login_required
def profile(request):
    return render(request, 'users/profile.html')

@login_required
def nouvelleListe(request):
    form = ListForm(request.POST)
    if form.is_valid():
        l = form.save()
        l.auteur.add(request.user)
        l.validee = False
        l.save()
        return editListe(request, l.id)
    return render(request, 'users/newList.html', locals())

# @login_required
def editListe(request, listeId):
    l = get_object_or_404(Liste, id=listeId)
    user = request.user
    if user not in l.auteur.all():
        return redirect('/')
    cats = Categorie.objects.all()
    for c in cats:
        c.crits = []
        c.crits.extend(Critere.objects.filter(Ville=l.ville, categorie=c))
        for crit in c.crits:
            crit.pros = Promesse.objects.filter(critere=crit, liste=l)
    if 'cancel' in request.POST:
        return redirect(liste, l.id)
    if 'save' in request.POST or 'saveandcontinue' in request.POST :
        l.nom = request.POST.get("nom", default=None) if request.POST.get("nom", default=None) != "" else None
        l.teteDeListe = request.POST.get("teteDeListe", default=None) if request.POST.get("teteDeListe",
                                                                                          default=None) != "" else None
        l.presentation = request.POST.get("presentation", default=None) if request.POST.get("presentation",
                                                                                            default=None) != "" else None
        l.couleur = request.POST.get("couleur", default=None) if request.POST.get("couleur",
                                                                                  default=None) != "" else None
        l.lienPhoto = request.POST.get("lienPhoto", default=None) if request.POST.get("lienPhoto",
                                                                                      default=None) != "" else None
        l.site = request.POST.get("site", default=None) if request.POST.get("site", default=None) != "" else None
        l.twitter = request.POST.get("twitter", default=None) if request.POST.get("twitter", default=None) != "" else None
        l.save()
        prios = request.POST.getlist('prio', default=None)
        newPrios = request.POST.getlist('new-prio', default=None)
        for p in Promesse.objects.filter(liste=l) : #Modification des promesses existantes
            edTPro = request.POST.get("t-"+str(p.id), default=None)
            edDPro = request.POST.get("d-"+str(p.id), default=None)
            if edTPro is not None:
                if edTPro == "":
                    p.delete()
                else :
                    p.titre = edTPro
                    if edDPro is not None :
                        p.description = edDPro
                    else:
                        p.description = ""
                    if str(p.id) in prios:
                        p.estUnePriorite = True
                    else:
                        p.estUnePriorite = False
                    p.save()
        for cri in Critere.objects.filter(Ville=l.ville): #Création de nouvelles promesses
            DescriptionPro = request.POST.get('newd-'+str(cri.id), default=None)
            titrePro = request.POST.get('newt-'+str(cri.id), default=None)
            if titrePro is not None and titrePro!='':
                p = Promesse(liste=l, titre=titrePro, description=DescriptionPro , critere=cri)
                if str(cri.id) in newPrios:
                    p.estUnePriorite = True
                else:
                    p.estUnePriorite = False
                p.save()
        if 'save' in request.POST :
            return redirect(liste, l.id)
        ancre=request.POST.get('saveandcontinue', default=None)
        if ancre is not None : return redirect('/edit/'+str(l.id)+'#'+str(ancre))
    return render(request, 'users/editListe.html', locals())


""" Old registration form (created with django form)
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Le compte a été crée {username}!  \n'
                                      f'Tu peux te connecter maintenant :)')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})
"""
