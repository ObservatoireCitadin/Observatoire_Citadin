# Application de comparaison de programmes municipaux


Application web permettant de comparer des programmes électoraux dans le cadre des élections municipales en France. Le projet est développé en Python en s'appuyant sur l'environnement Django.
 

## Installation

# 

1\. Cloner le dépôt :

```bash

git clone https://github.com/jcordier/ProgrammesMunicipales.git
```

2\. Installer les dépendances :

```bash

pip install -r requirements.txt

```

3\. Appliquer les migrations :

```bash

python manage.py migrate

```
## Exécution

 ```bash
python manage.py runserver
```

## Versions utilisées

Les dépendances complètes sont disponibles dans le fichier `requirements.txt`. Les versions actuellement présentes sont anciennes et destinées à une future mise à jour.

## Structure du projet

- `src/` : code applicatif

- `manage.py` : commande principale Django

- `requirements.txt` : dépendances du projet

## Auteurs
Projet initialement développé par Jérémy CORDIER, Rémi CAILLATE et Armando FEMAT.
