import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from datetime import datetime, timedelta


def exctraction_datas(driver):
    table=driver.find_element(By.ID,"economicCalendarTable")
    body=table.find_element(By.TAG_NAME,"tbody")
    trs=body.find_elements(By.CLASS_NAME,"economicCalendarRow")
    liste_annonce=[]
    for tr in trs:


        tds=tr.find_elements(By.TAG_NAME,"td")
        annonce={}
        for i,td in enumerate(tds):
            #Date
            if i==0:
                div=td.find_element(By.TAG_NAME,"div")
                annonce["Date"]=div.get_attribute("data-calendardatetd")

            elif i==1:
                pass

            #Flag nom du pays
            elif i==2:
                element=td.find_element(By.TAG_NAME,"i")

                data=element.get_attribute("title")
                annonce["Pays"]=data
            #Devise
            elif i==3:
               annonce["Devise"]=td.text
            #Nom annonce et mois de la data
            elif i==4:
                try:
                    nom_annonce=td.find_element(By.CSS_SELECTOR, "a.calendar-event-link").text
                    nom_mois=td.find_element(By.TAG_NAME,"span").text
                    annonce["nom_annonce"]=f"{nom_annonce} {nom_mois}"
                except:pass

            #Impact
            elif i==5:
                try:
                    div = td.find_element(By.TAG_NAME, "div")
                    annonce["Impact"] = div.text
                except:
                    pass
            #Previous
            elif i==6:
                try:
                    previous_annonce=td.find_element(By.TAG_NAME,"span").text
                    annonce["Précédent"]=previous_annonce
                except:pass
            #Consensus
            elif i==7:
                try:
                    concensus=td.find_element(By.TAG_NAME,"div").text
                    annonce['Concensus']=concensus
                except:pass
            #Actual
            elif i==8:
                try:
                    span = td.find_element(By.TAG_NAME, "span")
                    actual=span.find_element(By.TAG_NAME,"span").text
                    annonce["acutal"]=actual
                except:pass
        liste_annonce.append(annonce)
        #print(annonce)

    return liste_annonce


def base_economic_calendar_scrapping(chemin_gecko_driver):
 #Chemin vers geckodriver
    geckodriver_path=chemin_gecko_driver
    # Configuration du pilote Firefoxw
    firefox_options = webdriver.FirefoxOptions()

    # Création de l'instance du navigateur Firefox
    driver = webdriver.Firefox( options=firefox_options)

    driver.get("https://www.myfxbook.com/fr/forex-economic-calendar")
    #Enelver l'element obsurcissant

    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    #Cliquer sur bouton pour accepter cookie
    element_open_calendar = driver.find_element(By.ID, 'dismissGdprConsentBannerBtn')
    element_open_calendar.click()


    driver.execute_script("window.scrollBy(0, 300);")
    return driver


#Ca à l'air bon maintenant wtf
def scrapping_annonce(year_left,month_left,year_right,month_right,jour_left,jour_right,filtre_data):
    liste_mois=["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août","Septembre","Octobre","Novembre","Décembre"]
    #Chemin vers geckodriver
    geckodriver_path="C:\\Users\\Baptiste\\Desktop\\Informatique\\Logiciel\\Geckodriver_selenium_pilote_firefox\\geckodriver.exe"
    # Configuration du pilote Firefoxw
    firefox_options = webdriver.FirefoxOptions()

    # Création de l'instance du navigateur Firefox
    driver = webdriver.Firefox( options=firefox_options)

    driver.get("https://www.myfxbook.com/fr/forex-economic-calendar")
    #Enelver l'element obsurcissant
    time.sleep(60)
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    #Cliquer sur bouton pour accepter cookie
    element_open_calendar = driver.find_element(By.ID, 'dismissGdprConsentBannerBtn')
    element_open_calendar.click()

    # Selection Annonce Impact and more
    element_filter = driver.find_element(By.XPATH,
                                         "/html/body/div[3]/div[6]/div/div/div/div/div/div/div/div/div[4]/div[2]/div[1]/div/div/div[1]/span/span[1]/span/ul/li/input")
    for filtre in filtre_data:
        element_filter.send_keys(filtre)
        time.sleep(10)
        webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()
    webdriver.ActionChains(driver).send_keys(Keys.ENTER).perform()

    # Faire défiler la page vers le bas de 500 pixels
    driver.execute_script("window.scrollBy(0, 300);")

    #Selectionner element pour afficher calendar  <i class="far fa-calendar-alt fa-lg"></i> |Xpath: //*[@id="calendarCustomBtn"]

    element_open_calendar = driver.find_element(By.ID,'calendarCustomBtn')
    element_open_calendar.click()

    ##CALENDAR SELECTION
    if 1==1:
        calendar_left = element_open_calendar.find_element(By.XPATH,
                                                           '/html/body/div[3]/div[6]/div/div/div/div/div/div/div/div/div[4]/div[2]/div[3]/div[2]')
        calendar_right = driver.find_element(By.XPATH,"/html/body/div[3]/div[6]/div/div/div/div/div/div/div/div/div[4]/div[2]/div[3]/div[3]")

    ####Selction Year
        # Selection Year left
        year_left_list = calendar_left.find_element(By.CLASS_NAME, "yearselect")
        year_left_list.click()
        select_year_left = Select(year_left_list)
        select_year_left.select_by_value(year_left)
        #Selection Year right
        year_right_list = calendar_right.find_element(By.CLASS_NAME, "yearselect")
        year_right_list.click()
        select_year_right = Select(year_right_list)
        select_year_right.select_by_visible_text(year_right)

    ####SelectionMonth+Day
       #Selection Month left
        month_left_list=calendar_left.find_element(By.CLASS_NAME,"monthselect")
        month_left_list.click()
        time.sleep(1)
        select_month_left=Select(month_left_list)
        select_month_left.select_by_value(str(liste_mois.index(month_left)))





        time.sleep(1)
        # Selection chiffre left
        tableau_chiffre_left = driver.find_element(By.XPATH,
                                                   "/html/body/div[3]/div[6]/div/div/div/div/div/div/div/div/div[4]/div[2]/div[3]/div[2]/div[1]/table/tbody")
        trs_left = tableau_chiffre_left.find_elements(By.TAG_NAME, "tr")
        element_jour_left = ""
        for row in trs_left:
            tds = row.find_elements(By.XPATH,
                                    ".//td[contains(@class, 'available') or contains(@class, 'weekend available')]")
            for td in tds:
                if td.text == jour_left:
                    element_jour_left = td
        element_jour_left.click()

        #Selection Mois right

        calendar_right = driver.find_element(By.XPATH,
                                             "/html/body/div[3]/div[6]/div/div/div/div/div/div/div/div/div[4]/div[2]/div[3]/div[3]")
        month_right_list = calendar_right.find_element(By.CLASS_NAME, "monthselect")
        month_right_list.click()
        time.sleep(2)
        select_month_right = Select(month_right_list)
        time.sleep(2)
        select_month_right.select_by_value(str(liste_mois.index(month_right)))




        #Selection chiffre droit
        tableau_chiffre_right = driver.find_element(By.XPATH,
                                                    "/html/body/div[3]/div[6]/div/div/div/div/div/div/div/div/div[4]/div[2]/div[3]/div[3]/div[1]/table/tbody")
        trs_right = tableau_chiffre_right.find_elements(By.TAG_NAME, "tr")
        element_jour_right = ""
        for row in trs_right:
            tds = row.find_elements(By.XPATH,
                                    ".//td[contains(@class, 'available') or contains(@class, 'weekend available')]")
            for td in tds:

                if td.text == (str(int(jour_right))):
                    element_jour_right = td


        element_jour_right.click()

    button_postuler=driver.find_element(By.XPATH,"/html/body/div[3]/div[6]/div/div/div/div/div/div/div/div/div[4]/div[2]/div[3]/div[4]/button[2]")
    button_postuler.click()

#selection et cliquer sur le bouton qui montre plus d'annonce

    time.sleep(1)
    while True:

        button_montrer_plus = driver.find_element(By.ID, "showMoreCalendarBtn")
        is_visible=button_montrer_plus.is_displayed()
        if is_visible:
            driver.execute_script("arguments[0].click();", button_montrer_plus)
        else:break
    time.sleep(3)
    liste_annonce=exctraction_datas(driver)
    #driver.quit()
    return liste_annonce


#[Date,#,nom du pays (<i> arg title),Devise(->td pas div),Nom annonce<a> +<span> précision du mois,Impact,Previous,Consensus<div>,acutual<span>,#]




#Ok c'est bon
def scrap_data_last_week():
    # Noms de mois en français
    noms_mois = [
        "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
    ]

    # Obtenez la date actuelle
    aujourd_hui = datetime.now()

    # Calculez le jour de la semaine actuel (0 = lundi, 6 = dimanche)
    jour_de_la_semaine_actuel = aujourd_hui.weekday()

    # Calculez le début de la semaine passée (en remontant jusqu'au lundi)
    date_lundi_semaine_passee = aujourd_hui - timedelta(days=jour_de_la_semaine_actuel + 7)


    # Calculez la date du vendredi de la semaine passée (en ajoutant 4 jours à la date du lundi)
    date_vendredi_semaine_passee = date_lundi_semaine_passee + timedelta(days=4)



    # Obtenir le mois en lettres et en français

    mois_lundi = noms_mois[date_lundi_semaine_passee.month - 1]
    mois_vendredi=noms_mois[date_vendredi_semaine_passee.month-2]
    datas=scrapping_annonce(year_left=str(date_lundi_semaine_passee.year),month_left=str(mois_lundi),year_right=str(date_vendredi_semaine_passee.year),
                              month_right=str(mois_vendredi),jour_left=str(date_lundi_semaine_passee.day),jour_right=str(date_vendredi_semaine_passee.day),filtre_data=["Haut","Moyen"])
    return datas



#Ok validé
def scrapping_semaine_pro():
    chemin="C:\\Users\\Baptiste\\Desktop\\Informatique\\Logiciel\\Geckodriver_selenium_pilote_firefox\\geckodriver.exe"
    driver=base_economic_calendar_scrapping(chemin)
    btn_next_week=driver.find_element(By.XPATH,'//*[@id="calendarNextWeekBtn"]')

    btn_next_week.click()
    time.sleep(5)
    datas=exctraction_datas(driver)
    driver.quit()
    return datas




    #return datas


