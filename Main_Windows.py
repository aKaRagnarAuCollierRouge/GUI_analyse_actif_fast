import sqlite3
import logging
from PySide6.QtCore import Qt, QDate

from Style import *
from window_change_values_defaults.window_change_values_default import Change_value_filtre_tri_window
from fonction_annexes import get_date_lundi_vendredi_next, lister_dossiers_et_fichiers
from web_scrapping_annonce import scrapping_semaine_pro, scrap_data_last_week, scrapping_annonce
from gestion_db import *
import sys
import pandas as pd
from script_recherche_paire import *
from PySide6.QtGui import QIcon, QColor, QAction, QPixmap
from PySide6.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QGridLayout, QTabWidget, QMessageBox, \
    QComboBox, QRadioButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem, QTextEdit, QDateEdit, QSpinBox, \
    QHBoxLayout
from fast_COT import *
from fast_sentiment import *
import os
import datetime
import json
from sentiment_txt_to_excel import *
import subprocess
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            # ----------------------------------PREPARATION DONNEES ET VARIABLES

            # ---->Prélevement variables base de donnée Droit COT
            conn = sqlite3.connect('db.db')
            cu = conn.cursor()
            now = datetime.datetime.now()
            cu.execute("SELECT Value FROM Valeurs_defaults WHERE Name = 'chemin_Cot'")
            row = cu.fetchone()
            chemin_COT=row[0]
            cu.execute("SELECT Value FROM Valeurs_defaults WHERE Name='Chemin_Annonces_datas'")
            row=cu.fetchone()
            chemin_annonces_datas=row[0]
            cu.execute("SELECT Name FROM 'Catégorie actifs'")
            d=cu.fetchall()
            liste_catégorie_actif=[ligne[0] for ligne in d]
            conn.close()

            # ******Creation df pour onglet COT*****
            data_dict = {}
            # Chargez le classeur Excel
            wb = openpyxl.load_workbook(chemin_COT, read_only=True)
            # Obtenez les noms des feuilles
            sheet_names = wb.sheetnames
            df = pd.read_excel(chemin_COT, sheet_name=sheet_names, engine="openpyxl")

            for sheet_name in sheet_names:

                if 'NET POSITION' in df[sheet_name]:
                    data_dict[sheet_name] = df[sheet_name]['NET POSITION']

            self.df_COT = pd.DataFrame(data_dict)
            self.df_COT_final = self.df_COT.dropna()
            self.dico_serie = {}
            for nom_colonne in self.df_COT_final:
                série = 0
                value_previous = ""
                sens = ""
                df_devise = self.df_COT_final[nom_colonne]
                for index, value in enumerate(df_devise):

                    if index == 0:
                        value_previous = value
                        série += 1
                    elif index == 1:
                        if value_previous < value:
                            sens = "BEARISH"
                            série += 1
                        elif value_previous > value:
                            sens = "BULLISH"
                            série += 1
                        elif value_previous == value:
                            sens = "NEUTRAL"
                            break
                        value_previous = value
                    else:
                        if sens == "BULLISH":
                            if value < value_previous:
                                série += 1
                                value_previous = value
                            else:
                                break
                        elif sens == "BEARISH":
                            if value > value_previous:
                                série += 1
                                value_previous = value
                            else:
                                break
                self.dico_serie[df_devise.name] = {"série": série, "sens": sens}

            # ---------------------CREATION LAYOUT PRINCIPALES-------------------------
            self.setWindowTitle("Récupération données")
            self.setWindowIcon(QIcon("éclaire.jpg"))
            self.setMinimumSize(400,300)
            # creation widgets
            self.W_COT=QWidget()
            self.W_Backtest_rapide=QWidget()
            self.W_Main = QWidget()
            self.W_sentiment_forex = QWidget()
            self.W_affichage_paire = QWidget()
            self.W_COT_affichage = QWidget()
            self.W_COT_série = QWidget()
            self.W_annonce_post_week=QWidget()
            self.W_annonce_week=QWidget()
            self.W_saisonnality=QWidget()
            self.W_saisonnality_image=QWidget()

            layout_COT_récupération=QGridLayout()
            layout_main = QGridLayout()
            layout_sentiment = QGridLayout()
            layout_affichage_paire = QGridLayout()
            layout_COT = QGridLayout()
            layout_série_COT = QGridLayout()
            layout_post_annonce=QGridLayout()
            layout_annonce_week=QGridLayout()
            layout_Saisonnality=QGridLayout()
            layout_Saisonnality_image=QGridLayout()
            # Création table et différents onglets
            self.tabs = QTabWidget()
            self.tabs.setTabPosition(QTabWidget.East)

            # Création d'une barre d'outils
            self.menuBar = self.menuBar()
            self.default_menu = self.menuBar.addMenu("&Changer valeurs defaults")
            self.change_default_value = QAction("Changer value trie et filtrage")
            self.default_menu.addAction(self.change_default_value)
            self.change_default_value.triggered.connect(self.fct_change_valeus_defaults)

            # ------------------------------------------------------------------------------







            # -----------------------------------------------------------------------------------------
            # Création widgets pour onglet "Récupération COT et sentiment forex

            self.Button_COT=QPushButton("Extraire Datas COT")
            self.Button_sentiment_forex = QPushButton("Récupérer sentiment forex")

            self.Button_data_last_week = QPushButton("Récupérer data last_week")

            self.Button_data_next_week = QPushButton("Récupérer annonce next week")


            # Création widget pour affichage sentiment
            self.Label_Paire_recherche = QLabel("Indiquez la paire à rechercher:")
            self.Paire_recherche = QLineEdit()
            self.Button_recherche = QPushButton("Lancer la recherche")
            self.Button_classement_force=QPushButton("Classement force Sentiment forex")
            self.label_mini_condition_sentiment=QLabel("Mini:")
            self.mini_condition_sentiment=QSpinBox()
            self.mini_condition_sentiment.setValue(0)
            self.mini_condition_sentiment.setMinimum(0)
            self.mini_condition_sentiment.setMaximum(100)
            self.label_max_condition_sentiment=QLabel("Maxi:")
            self.max_condition_sentiment=QSpinBox()
            self.max_condition_sentiment.setMinimum(0)
            self.max_condition_sentiment.setMaximum(100)
            self.max_condition_sentiment.setValue(100)
            self.label_exclure_exotique=QLabel("Exclure les paires exotiques?")
            self.radio_exclure_yes_paire_exotique=QRadioButton("Yes")
            self.radio_exclure_yes_paire_exotique.setChecked(True)
            self.radio_exclure_no_paire_exotique=QRadioButton('No')


            self.Resultat_recherche = QTextEdit()
            self.Resultat_recherche.setFrameStyle(QTextEdit.NoFrame)
            self.Resultat_recherche.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

            # Création widget dans table_COT
            # Récupération Data pour COT

            Liste_paire = ["", 'USD', 'EUR', 'GBP', 'CAD', 'CHF', 'AUD', 'NZD', 'JPY', 'GOLD', 'SILVER', 'BTC', 'ETH',
                           'S&P500', 'MXN', 'ZAR', 'BRL']

            self.Devise_1 = QComboBox()
            self.Devise_1.addItems(Liste_paire)
            self.Devise_2 = QComboBox()
            self.Devise_2.addItems(Liste_paire)

            self.table_COT = QTableWidget()
            self.table_COT.setColumnCount(2)
            self.table_COT.setRowCount(self.df_COT_final.shape[0])
            self.table_COT.setEditTriggers(QTableWidget.NoEditTriggers)
            self.table_COT.setSelectionMode(QTableWidget.NoSelection)
            self.fig, self.ax = plt.subplots()
            self.canvas = FigureCanvas(self.fig)
            self.fig.set_facecolor('black')


            # Creation widget pour  layout_serie_cot
            self.Label_série_mini = QLabel("Série_minimum:")
            self.série_mini = QComboBox()
            item_combox = [str(i) for i in range(10)]
            self.série_mini.addItems(item_combox)
            self.série_mini.setCurrentIndex(6)
            self.Tab_serie = QTableWidget()
            self.Tab_serie.setEditTriggers(QTableWidget.NoEditTriggers)
            self.Tab_serie.setSelectionMode(QTableWidget.NoSelection)
            self.fig2, self.ax2 = plt.subplots()
            self.canvas2 = FigureCanvas(self.fig2)
            self.fig2.set_facecolor('black')


            #Widget pour layout postweek
            wb=openpyxl.load_workbook(chemin_annonces_datas)
            sheets=wb.sheetnames
            self.Label_combobox_post_annonce=QLabel("Selection Devise: ")
            self.Combo_devise_post_annonce=QComboBox()
            self.Combo_devise_post_annonce.addItems(sheets)
            self.Tab_post_week=QTableWidget()
            self.Tab_post_week.setEditTriggers(QTableWidget.NoEditTriggers)
            self.Tab_post_week.setSelectionMode(QTableWidget.NoSelection)

            #création widget annonce_week
            self.Label_combobox_impact_annonce = QLabel("IMPACT:")
            self.Combo_devise_impact_annonce = QComboBox()
            self.Combo_devise_impact_annonce.addItems(["Haut","Moyen","Faible"])
            self.Tab_annonce_week = QTableWidget()
            self.Tab_annonce_week.setEditTriggers(QTableWidget.NoEditTriggers)
            self.Tab_annonce_week.setSelectionMode(QTableWidget.NoSelection)
            # Redimensionnez les colonnes pour qu'elles correspondent au contenu


            #saisonnality
            self.label_selection_categories_actifs=QLabel("Selectionner Catégorie Actifs")
            self.Cb_selection_categories=QComboBox()
            self.Cb_selection_categories.addItems(liste_catégorie_actif)
            self.label_selection_actif=QLabel("Selectionner l'Actif")
            self.Cb_selection_actifs=QComboBox()
            self.label_select_date_season=QLabel()
            self.select_date_season=QComboBox()
            self.select_date_season.addItems(["5","10","15","20","25","30","40","50"])
            self.label_recession=QLabel("Prendre en compte les recessions dans le calcul:")
            self.radio_yes_recession=QRadioButton('Yes')
            self.radio_yes_recession.setChecked(True)
            self.radio_no_recession=QRadioButton("No")
            self.Btn_graphique_saisonnality=QPushButton("Créer la saisonnalité")
            self.fig_season, self.ax_season = plt.subplots()
            self.canvas_season = FigureCanvas(self.fig_season)
            self.fig_season.set_facecolor('black')

            #Saisonnality image

            self.chemin_saisonnalité = os.path.join(os.path.dirname(os.path.abspath(__file__)),"dossier_saisonnality")
            self.dico_folder_file_saisonality=lister_dossiers_et_fichiers(self.chemin_saisonnalité)
            categories=[categorie for categorie in self.dico_folder_file_saisonality]
            self.label_catégorie_actif_image=QLabel("Selectionne catégorie actif:")
            self.Cb_catégorie_actif_image=QComboBox()
            self.Cb_catégorie_actif_image.addItems(categories)
            self.label_select_actif_image=QLabel("Selectionne actif:")
            self.Cb_select_actif_image=QComboBox()
            self.Btn_saisonality_image=QPushButton("Saisonnalité image")
            self.Image_saisonnality=QLabel()


 # -----------------------Ajout widget dans layout----------------------------

            #ajout widget pour layout_annonce_week
            layout_annonce_week.addWidget(self.Label_combobox_impact_annonce)
            layout_annonce_week.addWidget(self.Combo_devise_impact_annonce)
            layout_annonce_week.addWidget(self.Tab_annonce_week)
            #ajout widget pour layout_post_annonce
            layout_post_annonce.addWidget(self.Label_combobox_post_annonce)
            layout_post_annonce.addWidget(self.Combo_devise_post_annonce)
            layout_post_annonce.addWidget(self.Tab_post_week)

            # ajout widget pour layout_serie_cot

            layout_COT.addWidget(self.Devise_1, 0, 0)
            layout_COT.addWidget(self.Devise_2, 0, 1)
            layout_COT.addWidget(self.table_COT, 1,0,2,2)
            layout_COT.addWidget(self.canvas, 3,0,2,2)
            # ajout widgets dans les layout Main
            layout_main.addWidget(self.Button_COT)
            layout_main.addWidget(self.Button_sentiment_forex)
            layout_main.addWidget(self.Button_data_next_week)
            layout_main.addWidget(self.Button_data_last_week)

            layout_série_COT.addWidget(self.Label_série_mini)
            layout_série_COT.addWidget(self.série_mini)
            layout_série_COT.addWidget(self.Tab_serie)
            layout_série_COT.addWidget(self.canvas2)
            # ajout widget recherche paire
            # Création du QGridLayout

            layout_affichage_paire.addWidget(self.Label_Paire_recherche, 0, 0)
            layout_affichage_paire.addWidget(self.Paire_recherche, 0, 1)
            layout_affichage_paire.addWidget(self.Button_recherche, 1, 0, 1, 2)
            layout_affichage_paire.addWidget(self.Button_classement_force, 2, 0, 1, 2)


            layout_affichage_paire.addWidget(self.label_mini_condition_sentiment, 3, 0)
            layout_affichage_paire.addWidget(self.mini_condition_sentiment, 3, 1)
            layout_affichage_paire.addWidget(self.label_max_condition_sentiment, 3, 2)
            layout_affichage_paire.addWidget(self.max_condition_sentiment, 3, 3)
            layout_affichage_paire.addWidget(self.label_exclure_exotique ,4,0)
            layout_affichage_paire.addWidget(self.radio_exclure_yes_paire_exotique,5,0)
            layout_affichage_paire.addWidget(self.radio_exclure_no_paire_exotique,6,0)
            layout_affichage_paire.addWidget(self.Resultat_recherche, 7, 0, 1, 7)

            layout_Saisonnality.addWidget(self.label_selection_categories_actifs)
            layout_Saisonnality.addWidget(self.Cb_selection_categories)
            layout_Saisonnality.addWidget(self.label_selection_actif)
            layout_Saisonnality.addWidget(self.Cb_selection_actifs)
            layout_Saisonnality.addWidget(self.label_select_date_season)
            layout_Saisonnality.addWidget(self.select_date_season)
            layout_Saisonnality.addWidget(self.label_recession)
            layout_Saisonnality.addWidget(self.radio_yes_recession)
            layout_Saisonnality.addWidget(self.radio_no_recession)
            layout_Saisonnality.addWidget(self.Btn_graphique_saisonnality)
            layout_Saisonnality.addWidget(self.canvas_season)

            #widget image_saisonnality
            layout_Saisonnality_image.addWidget(self.label_catégorie_actif_image)
            layout_Saisonnality_image.addWidget(self.Cb_catégorie_actif_image)
            layout_Saisonnality_image.addWidget(self.label_select_actif_image)
            layout_Saisonnality_image.addWidget(self.Cb_select_actif_image)
            layout_Saisonnality_image.addWidget(self.Btn_saisonality_image)
            layout_Saisonnality_image.addWidget(self.Image_saisonnality)



            self.W_COT_série.setLayout(layout_série_COT)
            self.W_Main.setLayout(layout_main)
            self.W_sentiment_forex.setLayout(layout_sentiment)
            self.W_affichage_paire.setLayout(layout_affichage_paire)
            self.W_COT_affichage.setLayout(layout_COT)
            self.W_annonce_post_week.setLayout(layout_post_annonce)
            self.W_annonce_week.setLayout(layout_annonce_week)
            self.W_saisonnality.setLayout(layout_Saisonnality)
            self.W_saisonnality_image.setLayout(layout_Saisonnality_image)
            self.tabs.addTab(self.W_Main, 'Récupération data')
            self.tabs.addTab(self.W_affichage_paire, 'recherche paire')
            self.tabs.addTab(self.W_COT_affichage, 'COT affichage')
            self.tabs.addTab(self.W_COT_série, "COT série")
            self.tabs.addTab(self.W_saisonnality, "Saisonnality")
            self.tabs.addTab(self.W_saisonnality_image,"Saisonnality image")
            self.tabs.addTab(self.W_annonce_week,"Annonce week")
            self.tabs.addTab(self.W_annonce_post_week,"Post week annonce")
            self.setCentralWidget(self.tabs)


            # connexion evenement au widget
            self.Button_COT.clicked.connect(self.récupération_cot)
            self.Button_sentiment_forex.clicked.connect(self.récupération_sentiment)
            self.Button_recherche.clicked.connect(self.script_recherche_paire)
            self.Devise_1.currentTextChanged.connect(self.Devise_change_COT)
            self.Devise_2.currentTextChanged.connect(self.Devise_change_COT)
            self.série_mini.currentTextChanged.connect(self.Série_change_COT)
            self.Button_data_last_week.clicked.connect(self.past_week_scrapping)
            self.Button_data_next_week.clicked.connect(self.next_week_scrapping)
            self.Combo_devise_impact_annonce.currentTextChanged.connect(self.change_combobox_impact_week)
            self.Combo_devise_post_annonce.currentTextChanged.connect(self.change_combobox_actif_post_week)
            self.Button_classement_force.clicked.connect(self.Classement_force_sentiment)
            #connexion saisonnality
            self.Cb_selection_categories.currentTextChanged.connect(self.change_categorie_actifs)
            self.Btn_graphique_saisonnality.clicked.connect(self.update_graphique_saisonnality)
            #connexion saisonnality image
            self.Btn_saisonality_image.clicked.connect(self.change_image_saisonnality)
            self.Cb_catégorie_actif_image.currentTextChanged.connect(self.change_cb_categorie_image_saisonnality)



#---------------Style
            liste_label=[self.label_exclure_exotique,self.label_recession,self.label_select_date_season,self.label_selection_categories_actifs,
                         self.label_selection_actif,self.Label_série_mini,self.Label_Paire_recherche,self.Label_combobox_post_annonce,
                         self.Label_combobox_impact_annonce,self.label_mini_condition_sentiment,self.label_max_condition_sentiment,
                         self.label_select_actif_image,self.label_catégorie_actif_image]
            liste_Button=[self.Button_COT,self.Button_recherche,self.Button_classement_force,self.Button_data_last_week,
                          self.Button_sentiment_forex,self.Button_data_next_week,self.Btn_graphique_saisonnality,
                          self.Btn_saisonality_image]

            for w in liste_Button:
                w.setStyleSheet(style_button)

            for w in liste_label:
                w.setStyleSheet(style_QLabel)
            #style page et tabs
            self.setStyleSheet(style_beige)
            self.tabs.setStyleSheet(style_onglet)

        def change_cb_categorie_image_saisonnality(self):
            categorie=self.Cb_catégorie_actif_image.currentText()
            self.Cb_select_actif_image.clear()
            self.Cb_select_actif_image.addItems(self.dico_folder_file_saisonality[categorie])
        def change_image_saisonnality(self):
            actif=self.Cb_select_actif_image.currentText()
            categorie=self.Cb_catégorie_actif_image.currentText()
            chemin=os.path.join(self.chemin_saisonnalité,categorie,actif)
            pixmap = QPixmap(chemin)
            self.Image_saisonnality.setPixmap(pixmap)
            self.Image_saisonnality.resize(pixmap.width(), pixmap.height())

        def change_categorie_actifs(self):
            actif=self.Cb_selection_categories.currentText()
            conn=sqlite3.connect("db.db")
            cu=conn.cursor()
            cu.execute(f"SELECT * FROM '{actif}'")
            d=cu.fetchall()
            liste_actif=[ligne[0] for ligne in d]
            self.Cb_selection_actifs.clear()
            self.Cb_selection_actifs.addItems(liste_actif)

        def update_graphique_saisonnality(self):
            #Récupération des données et calcul de la volatilité
            now=datetime.datetime.now()
            year_season=self.select_date_season.currentText()
            actif=self.Cb_selection_actifs.currentText()
            conn=sqlite3.connect("db.db")
            cu=conn.cursor()
            cu.execute(f"SELECT date,open,close FROM '{actif}'")
            rows=cu.fetchall()
            df = pd.DataFrame(rows, columns=['date','open', 'close'])
            df["date"]=pd.to_datetime(df["date"])
            #réajustement des dates
            df['diff'] = df['date'].diff()

            # Identifier les dates qui nécessitent un ajustement (différence supérieure à 1 jour)
            dates_a_ajuster = df[df['diff'] > pd.Timedelta(days=1)]['date']

            # Ajuster les dates nécessaires (par exemple, ajouter un jour)
            for date in dates_a_ajuster:
                df.loc[df['date'] == date, 'date'] = date + pd.Timedelta(days=1)

            # Supprimer la colonne 'diff' qui n'est plus nécessaire
            df = df.drop(columns=['diff'])
            df['date'].iloc[0] = df['date'].iloc[0] + pd.Timedelta(days=1)

        #calcul de la volatilité
            df["volatilité"]=df['open']-df["close"]

            #Exclusion de certaines années
            if year_season!="all":
                date_season=now-datetime.timedelta(days=(365*int(year_season)))
                df_final = df[df['date'] >=date_season]
            # Exclusion des recession
            if self.radio_yes_recession.isChecked():
                cu.execute(f"SELECT Début,Fin FROM 'Récession US'")
                rows=cu.fetchall()
                for row in rows:
                    Début=datetime.datetime.strptime(row[0], '%Y-%m-%d')
                    Fin=datetime.datetime.strptime(row[1], '%Y-%m-%d')
                    df_final=df_final[(df_final['date'] < Début) | (df_final['date'] >= Fin)]
            conn.close()
            #Calcul de la moyenne de volatilité par mois
            df_final['month']=df_final['date'].dt.month

            # Groupez les données par mois, puis calculez la moyenne de la volatilité
            moyenne_volatilite_par_mois = df_final.groupby('month')['volatilité'].mean().reset_index()

            # Renommez la colonne 'month' pour plus de clarté (facultatif)
            moyenne_volatilite_par_mois = moyenne_volatilite_par_mois.rename(columns={'month': 'mois'})



            #Mise à jour du graphique
            months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
            self.ax_season.clear()
            # Créez un graphique en barres
            colors = ['g' if v >= 0 else 'r' for v in moyenne_volatilite_par_mois['volatilité']]
            self.ax_season.bar(moyenne_volatilite_par_mois["mois"], moyenne_volatilite_par_mois["volatilité"], color=colors, alpha=0.7)
            self.ax_season.set_xlabel('Mois',color="orange")
            self.ax_season.set_ylabel('Volatilité Moyenne',color="orange")
            self.ax_season.set_title(f'{actif} {year_season}Y',color="red")
            self.ax_season.set_xticks(moyenne_volatilite_par_mois['mois'])
            self.ax_season.set_xticklabels(months, color='white')
            self.ax_season.tick_params(axis='both', colors='white')
            self.ax_season.yaxis.set_major_locator(plt.AutoLocator())
            self.canvas_season.draw()







        def fct_change_valeus_defaults(self):
            self.w = Change_value_filtre_tri_window()
            self.resize(300, 300)
            self.w.show()


        def Classement_force_sentiment(self):
            phrase=classement_force_sentiment_forex()
            self.Resultat_recherche.setText(phrase)

        def change_combobox_impact_week(self):
            # Effacer toutes les cellules du tableau
            self.Tab_annonce_week.clearContents()
            # Réinitialiser le nombre de lignes à zéro
            self.Tab_annonce_week.setRowCount(0)
            db=sqlite3.connect("db.db")
            conn=db.cursor()
            impact=self.sender().currentText()
            if impact=="Faible":
                requête="SELECT * FROM Annonce_semaine"
            elif impact=="Moyen":
                requête="SELECT * FROM Annonce_semaine WHERE Impact='MOYEN' OR Impact='HAUT'"
            else:
                requête="SELECT * FROM Annonce_semaine WHERE Impact='HAUT'"
            conn.execute(requête)
            datas=conn.fetchall()
            db.close()
            # Insérer les données ligne par ligne dans le QTableWidget
            headers = ['Date', 'Heure','Impact', 'Devise', 'Pays', 'Nom_annonce', 'Précédent', 'Concensus']
            self.Tab_annonce_week.setColumnCount(len(headers))
            self.Tab_annonce_week.setHorizontalHeaderLabels(headers)

            # Correspondance entre les noms d'attributs dans la base de données et les noms de colonnes
            correspondance_attributs = {
                'Date': 4,
                'Heure': 5,
                'Devise': 0,
                'Pays': 8,
                'Nom_annonce': 2,
                'Précédent': 6,
                'Concensus': 7,
                "Impact":1

            }
            now = datetime.datetime.now()
            for resultat in datas:

                row_index = self.Tab_annonce_week.rowCount()
                self.Tab_annonce_week.insertRow(row_index)

                for col_index, nom_colonne in enumerate(headers):
                    attribut_index = correspondance_attributs[nom_colonne]
                    valeur = resultat[attribut_index]
                    item = QTableWidgetItem(str(valeur))  # Convertir en str pour éviter les erreurs
                    self.Tab_annonce_week.setItem(row_index, col_index, item)
                    if nom_colonne=="Impact":
                        if valeur=="HAUT":
                            item.setBackground(QColor(242, 75, 34))
                        elif valeur=="MOYEN":
                            item.setBackground(QColor(235, 181, 57))
                        elif valeur=="FAIBLE":
                            item.setBackground(QColor(57, 189, 88))
                    elif nom_colonne=="Date":

                        valeur_dt=datetime.datetime.strptime(valeur,"%Y-%m-%d")
                        if valeur_dt==now:
                            item.setBackground(QColor(242, 75, 34))
                        elif valeur_dt<now:
                            item.setBackground(QColor(163,164,162))

            self.Tab_annonce_week.resizeColumnsToContents()

        def change_combobox_actif_post_week(self):
            conn = sqlite3.connect('db.db')
            cu = conn.cursor()
            cu.execute("SELECT Value FROM Valeurs_defaults WHERE Name = 'Chemin_Annonces_datas'")
            row = cu.fetchone()
            chemin_annonces_datas= row[0]
            # Effacer toutes les cellules du tableau
            self.Tab_post_week.clearContents()
            # Réinitialiser le nombre de lignes à zéro
            self.Tab_post_week.setRowCount(0)

            sheet_name=self.sender().currentText()
            df=pd.read_excel(chemin_annonces_datas,engine="openpyxl",sheet_name=sheet_name)
            # Convertir le DataFrame en une liste de listes
            data_list = df.values.tolist()
            # Configurer les en-têtes de colonnes
            self.Tab_post_week.setColumnCount(len(df.columns))
            self.Tab_post_week.setHorizontalHeaderLabels(df.columns)
            # Insérer les données dans le QTableWidget
            for row, row_data in enumerate(data_list):
                row_index = self.Tab_post_week.rowCount()
                self.Tab_post_week.insertRow(row_index)
                for col, cell_data in enumerate(row_data):
                    item = QTableWidgetItem(str(cell_data))
                    self.Tab_post_week.setItem(row, col, item)


        def next_week_scrapping(self):

            datas=scrapping_semaine_pro()
            date_first_annonce = datetime.datetime.strptime(datas[1]["Date"], "%Y-%m-%d %H:%M:%S.%f")
            date_last_annonce = datetime.datetime.strptime(datas[-1]["Date"], "%Y-%m-%d %H:%M:%S.%f")


            remove_data()
            insert_next_annonce(datas)



        def past_week_scrapping(self):
            lundi_past, vendredi_past = get_date_lundi_vendredi_next()
            datas = scrap_data_last_week()
            conn=sqlite3.connect("db.db")
            cu=conn.cursor()
            r="SELECT Value FROM Valeurs_defaults WHERE Name=='Chemin_annonces_datas'"
            row=cu.execute(r)
            chemin_excel=row.fetchone()[0]
            insert_week_post_annonce(datas,chemin_excel)

# -------------------------------------------------Fct pour série

        def update_cavenas2(self):
            couleurs = ['blue', 'green', 'red', 'c', 'm', 'y', 'k', 'w', 'orange', 'purple', 'pink', 'brown', 'violet',
                        'lightblue', 'gold', 'lime', 'gray', 'olive', 'navy', 'blue', 'green', 'red', 'c', 'm', 'y',
                        'k', 'w', 'orange', 'purple', 'pink', 'brown', 'violet',
                        'lightblue', 'gold', 'lime', 'gray', 'olive', 'navy']
            styles_ligne = ['-', '--', ':', '-.', 'solid', 'dashed', 'dashdot', 'dotted', '-', '--', ':', '-.', 'solid',
                            'dashed', 'dashdot', 'dotted', '-', '--', ':', '-.', 'solid', 'dashed', 'dashdot', 'dotted']
            data = []  # Liste pour stocker les données de toutes les courbes
            column_names = []  # Liste pour stocker les noms des en-têtes de colonnes

            for col in range(self.Tab_serie.columnCount()):
                column_data = []
                column_name = self.Tab_serie.horizontalHeaderItem(col).text()
                column_names.append(column_name)

                for row in reversed(range(self.Tab_serie.rowCount())):
                    item = self.Tab_serie.item(row, col)
                    if item is not None:
                        column_data.append(float(item.text()))
                    else:
                        column_data.append(0.0)

                data.append(column_data)

            self.ax2.clear()

            for col, column_data in enumerate(data):
                self.ax2.plot(range(1, len(column_data) + 1), column_data, label=column_names[col], color=couleurs[col],
                              linestyle=styles_ligne[col])

            self.ax2.tick_params(axis='both', colors='white')
            self.ax2.set_xlabel('Semaines passées', fontsize=10, color="white")
            self.ax2.set_ylabel('Lots (milliers)', fontsize=10, color="white")
            self.ax2.set_title("COT Série ", fontsize=13, color="orange")
            self.ax2.legend()

            self.canvas2.draw()



        def Série_change_COT(self):
            sender = self.sender()
            nb_série_mini = int(sender.currentText())
            dico_série_mini = {}
            for paire, dico in self.dico_serie.items():
                if dico["série"] >= nb_série_mini:
                    dico_série_mini[paire] = self.df_COT_final[paire]
            df = pd.DataFrame(dico_série_mini)
            df_serie_mini = df.dropna()

            nb_row, nb_columns = df_serie_mini.shape
            self.Tab_serie.setColumnCount(nb_columns)
            self.Tab_serie.setRowCount(nb_row)

            for col, nom_colonne in enumerate(df.columns):
                colonne = df_serie_mini[nom_colonne]
                série = self.dico_serie[nom_colonne]["série"]
                sens = self.dico_serie[nom_colonne]['sens']
                header_item = QTableWidgetItem(nom_colonne)
                self.Tab_serie.setHorizontalHeaderItem(col, header_item)
                for row, valeur in enumerate(colonne):
                    item = QTableWidgetItem(str(round(valeur, 3)))
                    self.Tab_serie.setItem(row, col, item)
                    if row < série:
                        if sens == "BULLISH":
                            item.setBackground(QColor(0, 255, 0))
                        elif sens == "BEARISH":
                            item.setBackground(QColor(255, 0, 0))
            self.update_cavenas2()


        #-----------------------------------------------
        def update_plot_cot(self):

            data = []
            column_names = [self.Devise_1.currentText(), self.Devise_2.currentText()]
            for col in range(self.table_COT.columnCount()):
                column_data = []
                for row in reversed(range(self.table_COT.rowCount())):
                    item = self.table_COT.item(row, col)
                    if item is not None:
                        column_data.append(float(item.text()))
                    else:
                        column_data.append(0.0)
                data.append(column_data)

            self.ax.clear()




            # Personnalisation des couleurs
            colors = ['red', 'green']

            # Personnalisation des styles de ligne
            line_styles = ['-', '--']

            for col, column_data in enumerate(data):
                self.ax.plot(range(1, len(column_data) + 1), column_data, label=column_names[col], color=colors[col],
                             linestyle=line_styles[col])
            self.ax.tick_params(axis='both', colors='white')  # Définit la couleur des chiffres et des axes en blanc
            self.ax.set_xlabel('Semaines passées',fontsize=10,color="white")
            self.ax.set_ylabel('Lots (milliers)',fontsize=10,color="white")
            self.ax.set_title("Comparaison COT",fontsize=13,color="orange")
            self.ax.legend()


            self.canvas.draw()
        def Devise_change_COT(self):
            # Obtenez le widget émetteur du signal

            sender_widget = self.sender()
            devise = sender_widget.currentText()
            série = self.dico_serie[devise]["série"]
            sens = self.dico_serie[devise]["sens"]
            header_item = QTableWidgetItem(devise)

            if sender_widget == self.Devise_1:
                self.table_COT.setHorizontalHeaderItem(0, header_item)
                for row in range(self.df_COT_final.shape[0]):
                    value = self.df_COT_final.at[row, devise]
                    item = QTableWidgetItem(str(round(value, 3)))
                    self.table_COT.setItem(row, 0, item)
                    if row < série:
                        if sens == "BULLISH":
                            item.setBackground(QColor(0, 255, 0))
                        elif sens == "BEARISH":
                            item.setBackground(QColor(255, 0, 0))
            elif sender_widget == self.Devise_2:
                self.table_COT.setHorizontalHeaderItem(1, header_item)
                for row in range(self.df_COT_final.shape[0]):
                    value = self.df_COT_final.at[row, devise]
                    item = QTableWidgetItem(str(round(value, 3)))
                    self.table_COT.setItem(row, 1, item)
                    if row < série:
                        if sens == "BULLISH":
                            item.setBackground(QColor(0, 255, 0))
                        elif sens == "BEARISH":
                            item.setBackground(QColor(255, 0, 0))
            self.update_plot_cot()
        # Probleme ca affiche la colonne USD à chaque fois==> je dois changer ca

        def script_recherche_paire(self):
            #modifier juste la condition
            mini=self.mini_condition_sentiment.value()
            maxi=self.max_condition_sentiment.value()
            mot = self.Paire_recherche.text()
            exclure_exotique=True
            if self.radio_exclure_no_paire_exotique.isChecked():
                exclure_exotique=False
            affichage = script_recherche_paire(mot,mini,maxi,exclure_exotique)
            self.Resultat_recherche.setText(affichage)

        def application_data_to_excel(self):
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setText("Voulez vous appliquer les données vers l'excel?")
            msg_box.setWindowTitle("Confirmation")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)

            result = msg_box.exec()

            if result == QMessageBox.Yes:
                report_sentiment_to_excel_previous_month()
                Bien_effectué = QMessageBox()
                Bien_effectué.setText("Bien appliqué")
                Bien_effectué.setWindowTitle('Les données ont bien été transférées')
                Bien_effectué.setStandardButtons(QMessageBox.Ok)
                Bien_effectué.exec()




                report_sentiment_to_excel_previous_month()

        # récupère data COT lorsque l'on clique sur le bouton COT

        def récupération_cot(self):
            # Créer une boîte de dialogue de confirmation
            conn = sqlite3.connect('db.db')
            cu = conn.cursor()
            cu.execute("SELECT Value FROM Valeurs_defaults WHERE Name = 'chemin_Cot'")
            row = cu.fetchone()
            chemin_COT = row[0]
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setText(f"Voulez vous récupérer Data COT à ce chemin {chemin_COT}")
            msg_box.setWindowTitle("Confirmation")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)

            result = msg_box.exec()

            if result == QMessageBox.Yes:

                main_COT(chemin_COT)
                self.df_COT_final
                Bien_effectué = QMessageBox()
                Bien_effectué.setText("Info bien récupéré")
                Bien_effectué.setWindowTitle('Bien récupéré!')
                Bien_effectué.setStandardButtons(QMessageBox.Ok)
                Bien_effectué.exec()
            elif result == QMessageBox.No:
                Pas_effectué= QMessageBox()
                Pas_effectué.setText("Veuillez changer le chemin du COT dans valeurs defaults")
                Pas_effectué.setStandardButtons(QMessageBox.Ok)
                Pas_effectué.exec()

        def récupération_sentiment(self):
            # Créer une boîte de dialogue de confirmation
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setText("Voulez vous récupérer Sentiment?")
            msg_box.setWindowTitle("Confirmation")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)

            result = msg_box.exec()

            if result == QMessageBox.Yes:
                main_sentiment()
                Bien_effectué = QMessageBox()
                Bien_effectué.setText("Info bien récupéré")
                Bien_effectué.setWindowTitle('Bien récupéré!')
                Bien_effectué.setStandardButtons(QMessageBox.Ok)
                Bien_effectué.exec()
            elif result == QMessageBox.No:
                pass

        # récupère data sentiment forex lorsque l'on clique sur le bouton sentiment forex


app = QApplication(sys.argv)
window = MainWindow()
window.showMaximized()

app.exec()
