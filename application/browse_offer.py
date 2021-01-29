from application import cursor
from application.accounts import get_logged_username

def get_catering_data():
    cursor.execute(f'SELECT nazwa, limit_zamowien, kontakt FROM bd2.firma_cateringowa, bd2.dane_kontaktowe WHERE bd2.dane_kontaktowe.firma_cateringowa_id = bd2.firma_cateringowa.id')
    return cursor.fetchall()

def get_reservation_data():
    cursor.execute(f'select miasto.nazwa, budynek.nazwa, ulica, numer, kod_pocztowy, numer_sali, miejsca_siedzace, powierzchnia, bd2.sala.id FROM bd2.miasto, bd2.budynek, bd2.sala WHERE bd2.miasto.id = bd2.budynek.miasto_id AND bd2.budynek.id = bd2.sala.budynek_id')

    data = cursor.fetchall()

    return data

def get_offer(catering_company_id):
    cursor.execute(f'SELECT bd2.produkt_spozywczy.id, cena, max_zamowienie, opis FROM bd2.produkt_spozywczy, bd2.firma_cateringowa WHERE bd2.firma_cateringowa.id = {catering_company_id} AND bd2.firma_cateringowa.id = bd2.produkt_spozywczy.firma_cateringowa_id')
    return cursor.fetchall()

def get_projects():
    logged_as = get_logged_username()
    cursor.execute(f'SELECT * FROM bd2.uzytkownik WHERE login = "{logged_as}"')

    temp = cursor.fetchall()
    if len(temp) == 0:
        return []

    worker_id = temp[0][7]

    cursor.execute(f"SELECT nazwa FROM bd2.projekt JOIN bd2.pracownik ON bd2.projekt.komorka_organizacyjna_id = bd2.pracownik.komorka_organizacyjna_id WHERE bd2.pracownik.id = '{worker_id}'")

    projects = cursor.fetchall()

    return projects