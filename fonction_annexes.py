from datetime import datetime,timedelta
import os
def get_date_lundi_vendredi_next():
    # Obtenez la date actuelle
    aujourd_hui=datetime.now()
    # Calculez le jour de la semaine actuel (0 = lundi, 6 = dimanche)
    jour_de_la_semaine_actuel = aujourd_hui.weekday()
    # Calculez le nombre de jours jusqu'au prochain lundi (en ajoutant les jours nécessaires)
    if jour_de_la_semaine_actuel==0:
        jours_jusquau_lundi_suivant=7
    else:
        jours_jusquau_lundi_suivant = (7 - jour_de_la_semaine_actuel) % 7
    # Calculez la date du prochain lundi
    lundi_suivant = aujourd_hui + timedelta(days=jours_jusquau_lundi_suivant)
    # Calculez la date du vendredi de la semaine suivante (en ajoutant 4 jours à la date du prochain lundi)
    vendredi_suivant = lundi_suivant + timedelta(days=4)

    return lundi_suivant,vendredi_suivant

def get_date_lundi_vendredi_previous():
    now=datetime.now()
    days_to_friday = (now.weekday() - 4) % 7
    if now.weekday()==4:
        vendredi=now - timedelta(days=days_to_friday+7)
    else:
        vendredi=now - timedelta(days=days_to_friday)
    lundi=vendredi-timedelta(days=4)

    return lundi,vendredi


def lister_dossiers_et_fichiers(chemin):
    resultats = {}

    for dossier, sous_dossiers, fichiers in os.walk(chemin):
        nom_dossier = os.path.basename(dossier)

        # Exclure le dossier "saisonnalité" des résultats
        if nom_dossier == "dossier_saisonnality":
            continue

        fichiers_avec_extension = [fichier for fichier in fichiers]

        resultats[nom_dossier] = fichiers_avec_extension

    return resultats





