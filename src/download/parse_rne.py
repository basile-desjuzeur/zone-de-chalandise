#%%

import numpy as np



class Etablissement :

    def __init__(self) -> None:
        self.codeApe = None
        self.siret = None
        self.nomCommercial = None
        self.codeInseeCommune = None
        self.adresse = None
        self.statut = None
        self.ferme = False
        self.enFrance = True


    def get_adresse(self,BlocAdresse):
        """
        returns
        - codeInseeCommune, adresse
        """

        # check si France
        if BlocAdresse.get("pays", "") != "FRANCE":
            self.enFrance = False
            return "", ""


        adresse_elements = [BlocAdresse.get(key, "") for key in ["numVoie", "typeVoie", "voie", "codePostal", "commune"]]

        # cas avec que des valeurs manquantes
        adresse = "" if adresse_elements == ["", "", "", "", ""] else " ".join(adresse_elements)

        return BlocAdresse.get("codeInseeCommune", ""), adresse



    # fonction pour remplir les attributs de l'établissement principal
    def fill_etablissementPrincipal(self, content):
        """
        content : dict["formality"]["content"]["personnePhysique"]
        """

        # est ce que l'établissement est fermé ?
        if content.get("etablissementPrincipal", {}).get("descriptionEtablissement",{}).get("dateEffetFermeture", "") != "":
            
            # si oui on ne le prend pas
            self.ferme = True
    
            # on ne return pas, pour pouvoir récupérer le code APE et le nom commercial
        
            
        self.codeInseeCommune,self.adresse = self.get_adresse(content.get("etablissementPrincipal", {}).get("adresse", {}))

        # l'affichage du code APE ne suit pas la même norme que la base sirene
        # rne : 4711F , sirene : 47.11F
        codeApe = content.get("identite", {}).get("entreprise", {}).get("codeApe","")
        self.codeApe = codeApe[:2] + "." + codeApe[2:]



        enseigne = content.get("etablissementPrincipal", {}).get("descriptionEtablissement", {}).get("enseigne", "")
        nomCommercial = content.get("identite", {}).get("entreprise", {}).get("denomination", "")
        self.nomCommercial = enseigne if len(enseigne) > len(nomCommercial) else nomCommercial



        self.siret = content.get("etablissementPrincipal", {}).get("descriptionEtablissement", {}).get("siret", "")


    def fill_autresEtablissements(self,content,i):
        """
        content : dict["formality"]["content"]["personnePhysique"]
        i : numéro de l'établissement
        """

        # est ce que l'établissement est fermé ?
        if content.get("autresEtablissements", [])[i].get("descriptionEtablissement",{}).get("dateEffetFermeture", "") != "":
            # si oui on ne le prend pas
            self.ferme = True
            #return


        self.codeInseeCommune,self.adresse = self.get_adresse(content.get("autresEtablissements", [])[i].get("adresse", {}))

        # l'affichage du code APE ne suit pas la même norme que la base sirene
        # rne : 4711F , sirene : 47.11F
        codeApe = content.get("autresEtablissements", [])[i].get("activites", [{}])[0].get("codeApe", "")
        self.codeApe = codeApe[:2] + "." + codeApe[2:]

        # on prend l'information la plus complète entre nom commercial et enseigne
        nomCommercial = content.get("autresEtablissements", [])[i].get("descriptionEtablissement", {}).get("nomCommercial", "")
        enseigne = content.get("autresEtablissements", [])[i].get("descriptionEtablissement", {}).get("enseigne", "")
        nomCommercial = nomCommercial if len(nomCommercial) > len(enseigne) else enseigne

        self.nomCommercial = nomCommercial
        self.siret = content.get("autresEtablissements", [])[i].get("descriptionEtablissement", {}).get("siret", "")

class Entreprise :

    def __init__(self, formality) -> None:

        # on ne prend que les personnes morales ou physiques (pas les indivisions ou autres)
        if formality.get("typePersonne", "") == 'P':
            self.typePersonne = "personnePhysique"
            self.content = formality.get("content", {}).get("personnePhysique", "")
            
        elif formality.get("typePersonne", "") == 'M':
            self.typePersonne = "personneMorale"
            self.content = formality.get("content", {}).get("personneMorale", "")

        else:
            raise ValueError("Ni personne physique ni personne morale (ex: indivision)")
        

        self.diffusionCommerciale = formality.get("diffusionCommerciale", False)
 

        # catégorisation des établissements

        self.etablissements = []

        if "etablissementPrincipal" in self.content.keys():
            self.etablissements.append(Etablissement())
            self.etablissements[-1].statut = "etablissementPrincipal"
            self.etablissements[-1].diffusionCommerciale = self.diffusionCommerciale
            self.etablissements[-1].fill_etablissementPrincipal(self.content)

        # TODO : ajouter les établissements modifiés
        if "etablissementModifie" in self.content.keys():
            self.etablissements.append(Etablissement())
            self.etablissements[-1].statut = "etablissementModifie"
            self.etablissements[-1].diffusionCommerciale = self.diffusionCommerciale

            self.etablissements[-1].fill_etablissementPrincipal(self.content)

        if "autresEtablissements" in self.content.keys():
            for i in range(len(self.content.get("autresEtablissements", []))):
                self.etablissements.append(Etablissement())
                self.etablissements[-1].statut = "autresEtablissements"
                self.etablissements[-1].diffusionCommerciale = self.diffusionCommerciale
                self.etablissements[-1].fill_autresEtablissements(self.content,i)

        else:
            raise ValueError("Pas d'établissement principal, modifié ou autre")
        

    attr_to_remove = ["statut","ferme","enFrance"]

    def etablissements_to_dict(self):
        """
        Amelioration des établissements
        - meilleur nom possible
        - ajout de diffusion commerciale
        - suppression des établissements fermés / hors France
        """
        # etablissements_list : liste des établissements sous forme de dict
        etablissements_list = []

        # on prend le meilleur nom possible (celui de l'entreprise si pas de nom commercial)
        for etablissement in [etablissement.__dict__ for etablissement in self.etablissements]:

            # on ne prend pas les établissements fermés ou hors France
            if etablissement["ferme"] or not etablissement["enFrance"]:
                continue

            if etablissement["nomCommercial"] == None or etablissement["nomCommercial"] == "":
                # udpate du nom commercial
                etablissement["nomCommercial"] = self.content.get("identite", {}).get("entreprise", {}).get("denomination", "")

            # suppresion des attributs inutiles (statut, ferme, enFrance)
            for attr in self.attr_to_remove:
                etablissement.pop(attr, None)


            # ajout a etablissement_list
            etablissements_list.append(etablissement)

        if etablissements_list == []:
            raise ValueError("Tous les établissements sont fermés ou hors France")

        return etablissements_list

def parse_formality(formality):
    """
    formality : dict["formality"]
    returns 
    a listof Etablissement for each open french establishment
    """
    try :
        return Entreprise(formality).etablissements_to_dict()
    
    except (ValueError) as e:
        return np.nan


# %%
