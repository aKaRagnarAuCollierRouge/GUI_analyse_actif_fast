import os
import sqlite3

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QLineEdit


class Change_value_filtre_tri_window(QWidget):

    def __init__(self):
        super().__init__()

        # Emplacement du répertoire du script Python
        emplacement_script = os.path.dirname(os.path.abspath(__file__))

        self.chemin=os.path.join(emplacement_script,"..","db.db")
        self.setWindowIcon(QIcon("C:\\Users\\Baptiste\\Documents\\Web_Scrapping\\GUI_Backtesting_fast\\Snake4.jpg"))
        conn=sqlite3.connect(self.chemin)
        cu = conn.cursor()
        cu.execute("SELECT Value FROM Valeurs_defaults WHERE Name = 'chemin_Cot'")
        row = cu.fetchone()
        chemin_COT = row[0]
        cu.execute("SELECT Value FROM Valeurs_defaults WHERE Name = 'Chemin_Annonces_datas'")
        row=cu.fetchone()
        chemin_Annonces_datas=row[0]
        cu.execute("SELECT Value FROM Valeurs_defaults WHERE Name = 'chemin_fichier_sentiment'")
        row = cu.fetchone()
        chemin_dossier_sentiment = row[0]

        conn.close()


        #Mise en place des widgets
        self.setWindowTitle("Changer value default filtrage-trie")
        layout = QGridLayout()
        self.label_Cot=QLabel("Modifier chemin COT:")
        self.line_chemin_cot=QLineEdit()
        self.line_chemin_cot.setText(chemin_COT)
        self.Btn_change_COT=QPushButton("Modifier")
        self.Btn_change_COT.clicked.connect(self.Modifier_chemin)

        self.label_chemin_annonces_datas=QLabel("Modifier chemin annonces datas")
        self.line_chemin_annonce_datas= QLineEdit()
        self.line_chemin_annonce_datas.setText(chemin_Annonces_datas)
        self.Btn_ajouter_annonces_datas=QPushButton("Modifier")
        self.Btn_ajouter_annonces_datas.clicked.connect(self.Modifier_chemin)

        self.label_chemin_folder_sentiment = QLabel("Modifier chemin dossier récupération sentiment")
        self.line_chemin_folder_sentiment = QLineEdit()
        self.line_chemin_folder_sentiment.setText(chemin_dossier_sentiment)
        self.Btn_ajouter_folder_sentiment = QPushButton("Modifier")
        self.Btn_ajouter_folder_sentiment.clicked.connect(self.Modifier_chemin)


        layout.addWidget(self.label_Cot)
        layout.addWidget(self.line_chemin_cot)
        layout.addWidget(self.Btn_change_COT)
        layout.addWidget(self.label_chemin_annonces_datas)
        layout.addWidget(self.line_chemin_annonce_datas)
        layout.addWidget(self.Btn_ajouter_annonces_datas)
        layout.addWidget(self.label_chemin_folder_sentiment)
        layout.addWidget(self.line_chemin_folder_sentiment)
        layout.addWidget(self.Btn_ajouter_folder_sentiment)

        self.setLayout(layout)

    def Modifier_chemin(self):
        if self.sender()==self.Btn_change_COT:
            nouveau_chemin=self.line_chemin_cot.text()
            name_value="chemin_COT"
        elif self.sender()==self.Btn_ajouter_annonces_datas:
            nouveau_chemin=self.line_chemin_annonce_datas.text()
            name_value="Chemin_Annonces_datas"
        elif self.sender()==self.Btn_ajouter_folder_sentiment:
            nouveau_chemin=self.line_chemin_folder_sentiment.text()
            name_value="chemin_fichier_sentiment"
        conn = sqlite3.connect(self.chemin)
        cu = conn.cursor()
        cu.execute("UPDATE Valeurs_defaults SET Value = ? WHERE Name = ?", (nouveau_chemin,name_value))
        conn.commit()
        conn.close()




