from application import cursor

def get_reservations(start, end, room):
    cursor.execute(
        f"SELECT * FROM bd2.rezerwacja WHERE sala_id = {int(room)} AND ((zakonczenie BETWEEN '{start}' AND '{end}') OR (rozpoczecie BETWEEN '{start}' AND '{end}'));")
    return cursor.fetchall()

def reserve(start, end, room, project, title):
    pass
