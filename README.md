# Présentation

Ce projet a pour but de cartographier des zones de chalandises, en particulier il vise à:

- estimer la population sous une aire donnée de France métropolitaine
- référencer les entreprises identifiées par leur code NAF (plus d'informations sur les codes NAF [ici](https://www.insee.fr/fr/information/2406147))

Un exemple : <a href="https://basile-desjuzeur.github.io/zone-de-chalandise/data/img/Strasbourg.html" onclick="window.open(this.href); return false;">Cartographie des hypermarchés à 1h de voiture de Lille</a>

Pour ce faire, il exploite des données publiques (voir [sources](#sources)) des institutions suivantes :

<p align="center">
  <img src="./data/img/sources_data.png" alt="Sources de données" width="200"/>
</p>

## Contenu du repo

- [Notebooks](./Notebooks/) : Les notebooks où les données ont été téléchargées et transformées.
- [src](./src) : Le script pour générer la carte
- Les données sont disponibles sur un repo privé

## Comment installer et utiliser

*(WIP)*

## Comment lire la carte ?

### 1. Population

La population estimée est la somme des populations des communes qui sont intégralement recouvertes par l'aire en bleu.

### 2. Etablissements

Les établissements affichées sont les établissements actifs référencés sur Sirene ou au RNE qui sont  situés dans des communes intégralement recouvertes par l'aire en bleu.

## 3. Données par Etablissement

Lorsque l'on passe la souris sur un établissement les informations suivantes sont affichées :

| Nom               | Description  |
|----------------------------|--------------|
| **Nom Commercial**         | Le nom de l'établissement             |
| **Adresse**                | L'adresse renseignée par l'établissement. Si l'établissement n'a pas renseigné d'adresse, c'est le code postal de la ville             |
| **Code APE**               | Le code Nomenclature des Activités Françaises (NAF) de l'établissement            |
| **SIRET**                  | L'identifiant SIRET de l'établisssement            |
| **Diffusion Commerciale**  | Si True, on peut utiliser les informations pour démarcher l'établissement, False sinon             |
| **Confiance dans la localisation**| Les établissements sont localisés avec un niveau de confiance variable (voir plus bas)       |
| **Lien Pappers**           |  Lien vers le site Pappers pour avoir plus d'informations sur l'établissement            |

Détail  sur la confiance dans la localisation :

| Code | Type de Voie      | Détails                                    | Score |
|------|-------------------|--------------------------------------------|-------|
| 11    | Voie Sûre         | Numéro trouvé                               | 100%     |
| 12   | Voie Sûre         | Position aléatoire dans la voie             | 80%     |
| 21   | Voie probable     | Numéro trouvé                               | 60%     |
| 22   | Voie probable     | Position aléatoire dans la voie             | 40%     |
| 33   | Voie inconnue      | Position aléatoire dans la commune          | 20%     |
| NaN  | Inconnu            | Position non renseignée dans le document de l'INSEE, localisation aléatoire dans la commune | 0%   |

**NB** : *Il se peut que les données ne soient pas exhaustives (tous les établissements ne sont pas nécessairement référencés, le jeu de données utilisé ici est issu de choix arbitraires), les informations délivrées ne doivent donc pas être pris pour argent comptant.*

## Sources

| Document                                                        | Source                                                | Producteur | Date d'édition des données | Licence                                         | Téléchargement |
|-----------------------------------------------------------------|-------------------------------------------------------|------------|-----------------------------|--------------------------------------------------|----------------|
| Liste des codes NAF                                             | INSEE                                                  | INSEE       | 08/03/2021                  | Licence Ouverte / Open Licence                    | HTPPS          |
| Population par commune                                          | Opendatasoft                                           | INSEE       | 07/01/2021                  | Licence Ouverte / Open Licence v2                 | HTPPS          |
| Localisation des communes                                       | La Poste                                               | La Poste    | 08/01/2024                  | Licence Ouverte / Open Licence                    | HTPPS          |
| Base Sirene des entreprises                                     | INSEE                                                  | INSEE       | 01/01/2024                  | Licence Ouverte / Open Licence v2.0               | HTPPS          |
| Registre National des Entreprises (RNE)                         | INPI                                                   | INPI        | 01/01/2024                  | Voir [licence](https://www.inpi.fr/sites/default/files/Proposition%20de%20licence%20informations%20publiques%20INPI%20%28PI%20et%20RNE%29%20en%20cours.pdf)                                   | SFTP           |

