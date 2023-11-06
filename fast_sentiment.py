import os.path
import sqlite3

import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup as bs
import requests
import openpyxl
from copy import copy
import datetime
import locale
from openpyxl.formula import Tokenizer
import sys
import datetime
import re
import locale


def récupération_données():
    url_fx_books = requests.get("https://www.myfxbook.com/fr/community/outlook")
    soup = bs(url_fx_books.text, 'html.parser')
    trs = soup.find_all('tr', class_='outlook-symbol-row')
    liste_données=[]
    for tr in trs:
        tbody=tr.find('tbody')
        tds=tbody.find_all('td')
        symbole=tds[0].text
        short=tds[2].text.rstrip('%')
        lot_short=tds[3].text.rstrip(" lots")
        long=tds[6].text.rstrip("%")
        lot_long=tds[7].text.rstrip(" lots")
        liste_données.append([symbole,long,short,lot_long,lot_short])
    return liste_données

def main_sentiment():
    locale.setlocale(locale.LC_TIME, 'fr_FR')
#chemin par default
#date pour trouver le bon dossier ou le créer

    conn=sqlite3.connect("db.db")
    cu=conn.cursor()
    r=cu.execute('Select Value FROM Valeurs_defaults WHERE Name="chemin_fichier_sentiment"')
    chemin_depot_default=r.fetchone()[0]

    #date pour trouver le bon dossier ou le créer
    date=datetime.datetime.now()
    year=date.year
    month=date.strftime("%B")
    day=date.day
    time=date.time()
    chemin_depot_default+=f"\\{year}"
    if not os.path.exists(chemin_depot_default):
        os.mkdir(chemin_depot_default)
    chemin_depot_default+=f"\\{month}"
    if not os.path.exists(chemin_depot_default):
        os.mkdir(chemin_depot_default)
    chemin_depot_default += f"\\{day}"
    if not os.path.exists(chemin_depot_default):
        os.mkdir(chemin_depot_default)
    nouveau_fichier=f"{chemin_depot_default}\\{date.hour}_{date.minute}.txt"





#Je dois concaténer l'année, le mois, le jour et à chaque fois regarder si il existe, s'il n'existe pas je dois créer le dossier
#Je dois ensuite créer un fichier txt nommée comme cela "Numero jour Heure_Minutes"


    liste_données=récupération_données()

    #Création et écriture dans le fichier texte
    with open(nouveau_fichier, 'w') as file:
        file.write(f"POSITIONNEMENT DUMB MONNEY | {day}{month}{year} à {time}\n\n")
        for symbole in liste_données:
            file.write(f"{symbole[0]}  Long:{symbole[1]}  Short:{symbole[2]} Lot_long:{symbole[3]} Lot_short:{symbole[4]}\n")

#-------------------------------------------------------------------------------------------

def récupération_sentiment_fx_books_sentiment():
    mdp="polmfpokm23!"
    mail="popoubelle2@gmail.com"
    url=f"https://www.myfxbook.com/api/login.json?email={mail}&password={mdp}"
    response=requests.get(url)
    if response.status_code == 200:
        # La requête a réussi, vous pouvez accéder aux données de la réponse en tant qu'objet JSON
        response_data = response.json()
        session=response_data["session"]
        sentiment_requete=f"https://www.myfxbook.com/api/get-community-outlook.json?session={session}"
        response=requests.get(sentiment_requete)
        data=response.json()









