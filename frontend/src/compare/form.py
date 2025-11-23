from django import forms
from compare.models import Ville, Liste
from dal import autocomplete
from django.shortcuts import get_object_or_404


class RechercheVille(forms.Form):
    ville = forms.ModelChoiceField(queryset=Ville.objects.all(),
                                   widget=autocomplete.ModelSelect2(url='ville-autocomplete'))
    ville.widget.attrs.update({'class': 'form-home'})
    # ville.widget.attrs.update(placeholder="Quelle est ta ville ?")



class FormContact(forms.Form):
    email = forms.EmailField()
    email.widget.attrs.update({'class': 'form-control'})
    email.widget.attrs.update(placeholder="Mon adresse mail")
    comment = forms.CharField(widget=forms.Textarea, required=False)
    comment.widget.attrs.update({'class': 'form-control'})
    comment.widget.attrs.update(placeholder="Nous sommes à l'écoute !")
    comment.widget.attrs.update(rows="4")
    inform = forms.BooleanField(label='Je souhaite être informé des grandes évolutions et actualités du projet',
                                required=False)

class FormContactBlack(forms.Form):
    email = forms.EmailField()
    email.widget.attrs.update({'class': 'form-control-black h-50'})
    email.widget.attrs.update(placeholder="Mon adresse mail")
    comment = forms.CharField(widget=forms.Textarea, required=False)
    comment.widget.attrs.update({'class': 'form-control-black'})
    comment.widget.attrs.update(placeholder="Nous sommes à l'écoute !")
    comment.widget.attrs.update(rows="4")
    inform = forms.BooleanField(label='Je souhaite être informé des grandes évolutions et actualités du projet',
                                required=False)

class FormInfo(forms.Form):
    email = forms.EmailField()
    email.widget.attrs.update(placeholder="Ton adresse email !")
    email.widget.attrs.update({'class': 'form-control-black form-group h-50'})
