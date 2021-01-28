from application import cursor

def get_offer():
    cursor.execute(f'SELECT nazwa, limit_zamowien FROM bd2.firma_cateringowa')
    return cursor.fetchall()
