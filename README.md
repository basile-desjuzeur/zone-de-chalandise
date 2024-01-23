# Présentation 

Ce projet a pour but de cartographier des zones de chalandises, en particulier il vise à:

- estimer la population sous une aire donnée de France métropolitaine
- référencer les entreprises identifiées par leur code NAF (plus d'informations sur les codes NAF [ici](https://www.insee.fr/fr/information/2406147))


Un exemple : <a href="https://basile-desjuzeur.github.io/zone-de-chalandise/img/Lille.html" onclick="window.open(this.href); return false;">Cartographie des hypermarchés à 1h de voiture de Lille</a>

Pour ce faire, il exploite des données publiques (voir source) des institutions suivantes :

<p align="center">
  <img src="./img/sources_data.png" alt="Sources de données" width="200"/>
</p>



# Contenu du repo

- [Notebooks](./Notebooks/) : Les notebooks où les données ont été téléchargées et transformées.
- [src](./src) : Le script pour générer la carte
- Les données sont disponibles sur un repo privé


# Comment installer & utiliser

*(WIP)*



# Comment lire la carte ?


## 1. Population

La population estimée est la somme des populations des communes qui sont intégralement recouvertes par l'aire en bleu.

## 2. Etablissements

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


## 4. Sources

| Document | Source     | Producteur |Date d'édition des données                      | Licence |Téléchargement |
|------|-------------------|------------|--------------------------------|----------| HTTPS |
|[liste des codes NAF]("../Données nationales/NAF.parquet") | [source](https://www.insee.fr/fr/information/2120875) | INSEE | 08/03/2021 | Licence Ouverte / Open Licence | HTTPS |
|[Population par commune]("../Données nationales/populationLocalisationCommunes.parquet") | [source](https://public.opendatasoft.com/explore/dataset/demographyref-france-pop-legale-commune-arrondissement-municipal-millesime/export/?flg=fr&disjunctive.reg_code&disjunctive.reg_name&disjunctive.com_arm_code&disjunctive.com_arm_name&disjunctive.dep_code&disjunctive.arrdep_code&disjunctive.epci_name&disjunctive.epci_code&disjunctive.dep_name&dataChart=eyJxdWVyaWVzIjpbeyJjb25maWciOnsiZGF0YXNldCI6ImRlbW9ncmFwaHlyZWYtZnJhbmNlLXBvcC1sZWdhbGUtY29tbXVuZS1hcnJvbmRpc3NlbWVudC1tdW5pY2lwYWwtbWlsbGVzaW1lIiwib3B0aW9ucyI6eyJmbGciOiJmciIsImRpc2p1bmN0aXZlLnJlZ19jb2RlIjp0cnVlLCJkaXNqdW5jdGl2ZS5yZWdfbmFtZSI6dHJ1ZSwiZGlzanVuY3RpdmUuY29tX2FybV9jb2RlIjp0cnVlLCJkaXNqdW5jdGl2ZS5jb21fYXJtX25hbWUiOnRydWUsImRpc2p1bmN0aXZlLmRlcF9jb2RlIjp0cnVlLCJkaXNqdW5jdGl2ZS5hcnJkZXBfY29kZSI6dHJ1ZSwiZGlzanVuY3RpdmUuZXBjaV9uYW1lIjp0cnVlLCJkaXNqdW5jdGl2ZS5lcGNpX2NvZGUiOnRydWUsImRpc2p1bmN0aXZlLmRlcF9uYW1lIjp0cnVlfX0sImNoYXJ0cyI6W3siYWxpZ25Nb250aCI6dHJ1ZSwidHlwZSI6ImxpbmUiLCJmdW5jIjoiQVZHIiwieUF4aXMiOiJjb21fYXJtX3BvcF9tdW4iLCJzY2llbnRpZmljRGlzcGxheSI6dHJ1ZSwiY29sb3IiOiIjRkY1MTVBIn1dLCJ4QXhpcyI6Imdlb195ZWFyIiwibWF4cG9pbnRzIjoiIiwidGltZXNjYWxlIjoieWVhciIsInNvcnQiOiIifV0sImRpc3BsYXlMZWdlbmQiOnRydWUsImFsaWduTW9udGgiOnRydWV9) | INSEE |07/01/2021 | Licence Ouverte / Open Licence v2 |HTTPS |
|[Localisation des communes]("../Données nationales/populationLocalisationCommunes.parquet") | [source](https://datanova.laposte.fr/datasets/laposte-hexasmal) | La Poste |08/01/2024 | Licence Ouverte / Open Licence |HTTPS |
|[Base Sirene des entreprises]("../Données nationales/RegistreNationalEtablissementsActifsRneSirene.parquet") | [source](https://www.data.gouv.fr/fr/datasets/base-sirene-des-entreprises-et-de-leurs-etablissements-siren-siret/) | INSEE |01/01/2024 | Licence Ouverte / Open Licence v2.0|HTTPS |
|[Registre National des Entreprises (RNE)]("../Données nationales/RegistreNationalEtablissementsActifsRneSirene.parquet") | [source](https://data.inpi.fr/) | INPI |01/01/2024 |voir [licence](https://www.inpi.fr/sites/default/files/Proposition%20de%20licence%20informations%20publiques%20INPI%20%28PI%20et%20RNE%29%20en%20cours.pdf)|SFTP |

