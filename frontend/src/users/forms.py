from django import forms
from django.forms import ModelForm
from compare.models import Ville, Liste
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from compare.models import Ville
from dal import autocomplete
from users.models import Profile
from django.contrib.auth import authenticate


class CustomUserCreationForm(forms.Form):
    username = forms.CharField(label='Nom d\'utilisateur', min_length=3, max_length=20)
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmation du mot de passe', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise ValidationError("Le nom d\'utilisateur existe déjà !")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise ValidationError('Email existe déjà !')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('Mot de passe différents !')
        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1'],
            #self.cleaned_data['ville'],
            #self.cleaned_data['is_list']

        )
        return user


class LoginForm(forms.Form):
    username = forms.CharField(label='Nom d\'utilisateur', min_length=3, max_length=20)
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)


'''
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise ValidationError("This field is required.")
        if User.objects.filter(email=self.cleaned_data['email']).count():
            raise ValidationError("Email is taken.")
        return self.cleaned_data['email']

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
'''

class ListForm(ModelForm):
    ville = forms.ModelChoiceField(queryset=Ville.objects.all(),
                                   widget=autocomplete.ModelSelect2(url='ville-autocomplete'))
    class Meta:
        model = Liste
        fields = ['ville', 'nom', 'couleur', 'teteDeListe', 'presentation', 'site', 'twitter']


