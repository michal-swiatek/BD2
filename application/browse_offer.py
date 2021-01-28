from application import cursor

def get_catering_data():
    cursor.execute(f'SELECT nazwa, limit_zamowien, kontakt FROM bd2.firma_cateringowa, bd2.dane_kontaktowe WHERE bd2.dane_kontaktowe.firma_cateringowa_id = bd2.firma_cateringowa.id')
    return cursor.fetchall()

def get_reservation_data():
    cursor.execute(f'select miasto.nazwa, budynek.nazwa, ulica, numer, kod_pocztowy, numer_sali, miejsca_siedzace, powierzchnia, bd2.sala.id FROM bd2.miasto, bd2.budynek, bd2.sala WHERE bd2.miasto.id = bd2.budynek.miasto_id AND bd2.budynek.id = bd2.sala.budynek_id')
    return cursor.fetchall()

# def get_catering_offer():
#
