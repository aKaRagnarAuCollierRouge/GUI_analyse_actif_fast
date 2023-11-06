style_beige="background-color: #faf3e0;"

style_onglet_normal="""QTabBar::tab { background-color: beige;color: #333; font-size: 16px;min-height: 50px;  } """
style_onglet_selected="""QTabBar::tab:selected { background-color: lightblue; font-weight: bold;min-height: 50px;  }"""
style_onglet=style_onglet_normal+style_onglet_selected
style_QLabel="QLabel { color: #FF6600; font-weight: bold; font-family: 'Helvetica'; font-size: 14px; font-weight: 100; }"
style_button="""
QPushButton {
    background-color: #3498db; /* Couleur de fond par défaut */
    color: white; /* Couleur du texte par défaut */
    border: 2px solid #3498db; /* Bordure par défaut */
    border-radius: 5px; /* Coins arrondis */
    padding: 10px 20px; /* Espacement intérieur */
}

QPushButton:hover {
    background-color: #2980b9; /* Couleur de fond au survol */
    border: 2px solid #2980b9; /* Bordure au survol */
}

QPushButton:pressed {
    background-color: #2074a0; /* Couleur de fond lorsque pressé */
    border: 2px solid #2074a0; /* Bordure lorsque pressé */
}
"""