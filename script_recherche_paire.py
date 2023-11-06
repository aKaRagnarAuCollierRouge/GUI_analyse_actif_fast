import os
import re
import sqlite3


def script_recherche_paire(mot,min,maxi,exclure_exotique=True):
     conn = sqlite3.connect("db.db")
     cu = conn.cursor()
     r = cu.execute('Select Value FROM Valeurs_defaults WHERE Name="chemin_fichier_sentiment"')
     chemin = r.fetchone()[0]
     for i in range(0,4):
          contenu_repertoire = os.listdir(chemin)
          # Trie les éléments par date de création (du plus récent au plus ancien)
          contenu_repertoire_trie = sorted(contenu_repertoire, key=lambda x: os.path.getctime(os.path.join(chemin, x)),
                                      reverse=True)
          chemin=chemin+"\\"+contenu_repertoire_trie[0]

     with open(chemin, 'r') as fichier:
          lignes = fichier.readlines()

          lignes_contenant_mot = []
          for ligne in lignes:
               if mot.upper() in ligne:
                    match = re.search(r'Long:(\d+)', ligne)
                    match2=re.search(r'Short:(\d+)',ligne)
                    if match and match2:
                         long_value = int(match.group(1))
                         short_value=int(match2.group(1))
                         if min < long_value < maxi or min<short_value<maxi:
                              lignes_contenant_mot.append(ligne)
          if exclure_exotique:
               liste_devise_exotique = ['XAU', "XAG", "TRY", "CNY", "SGD", "NOK", "CNK", "HUF", "SEK", "PLN", "MXN",
                                        "THB","ZAR", "CNH","XPT"]
               lignes_contenant_mot = [item for item in lignes_contenant_mot if
                                       not any(word in item for word in liste_devise_exotique)]
          affichage_complet="".join(lignes_contenant_mot)
     return affichage_complet



#----------------------------------------------------------------------------------------------------------------
def ligne_devise(devise):
     conn = sqlite3.connect("db.db")
     cu = conn.cursor()
     r = cu.execute('Select Value FROM Valeurs_defaults WHERE Name="chemin_fichier_sentiment"')
     chemin = r.fetchone()[0]
     liste_devises=["CAD","EUR","GBP","USD","JPY","CHF","AUD","NZD"]
     for i in range(0,4):
          contenu_repertoire = os.listdir(chemin)
          # Trie les éléments par date de création (du plus récent au plus ancien)
          contenu_repertoire_trie = sorted(contenu_repertoire, key=lambda x: os.path.getctime(os.path.join(chemin, x)),
                                      reverse=True)
          chemin=chemin+"\\"+contenu_repertoire_trie[0]

     with open(chemin, 'r') as fichier:
          lignes = fichier.readlines()
          for ligne in lignes:
               lignes_contenant_mot = [ligne for ligne in lignes if devise.upper() in ligne]
     liste_lignes=[]
     for ligne in lignes_contenant_mot:
          devise_1=ligne[0:3]
          devise_2=ligne[3:6]
          if devise_1 in liste_devises and devise_2 in liste_devises:
               liste_lignes.append(ligne)

     return liste_lignes


# Fonctions pour classer la force de chaque devise en fonction du sentiment forex

def traitement_ligne_paire(ligne_paire,devise):
     Paire=ligne_paire[:6]
     match = re.search(r'Long:(\d+)',ligne_paire)
     long_value=None
     if match:
          long_value=int(match.group(1))
     if devise==Paire[:3]:
          paire_principale=True
     else:
          paire_principale=False
     if paire_principale:
          paire_secondaire=Paire[3:]
          if long_value<50:
               return [True,paire_secondaire]
          else: return [False,paire_secondaire]
     else:
          paire_secondaire=Paire[:3]
          if long_value>50:
               return [True,paire_secondaire]
          else:return [False,paire_secondaire]


def classement_force_sentiment_forex():
     liste_paire=["EUR","GBP","USD","CAD","NZD","AUD","CHF","JPY"]
     dict_paires={}
     for paire in liste_paire:
          dict_paires[f"{paire}"]={"compteur":0,"Supérieur":[],"Inférieur":[]}

     #Classement des forces et compteur
     for devise in dict_paires:
          lignes_paires=ligne_devise(devise)
          #CADCHF  Long:21  Short:79 Lot_long:1453.62 Lot_short:5465.37
          for ligne_paire in lignes_paires:
               t=traitement_ligne_paire(ligne_paire,devise)
               if t[0]:
                    dict_paires[f"{devise}"]["compteur"]+=1
                    dict_paires[f"{devise}"]["Supérieur"].append(t[1])
               else:
                    dict_paires[f"{devise}"]["Inférieur"].append(t[1])

     # Triez le dictionnaire en fonction des compteurs
     paires_triees = sorted(dict_paires.items(), key=lambda x: x[1]["compteur"], reverse=True)
     phrase=''
     for paire in paires_triees:
          phrase+=f"{paire[0]}({paire[1]['compteur']})>"

     return phrase[0:-1]
# Ok la fonction est interressante je dois l'implementer dans un onglet, je peux aussi le faire mes avec les données
# de webscrapping



















