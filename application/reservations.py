from application import cursor

last_reservation = 1


def get_reservations(start, end, room):
    cursor.execute(
        f"SELECT * FROM bd2.rezerwacja WHERE sala_id = {int(room)} AND ((zakonczenie BETWEEN '{start}' AND '{end}') OR (rozpoczecie BETWEEN '{start}' AND '{end}'));")
    return cursor.fetchall()


def create_order(products, reservation_id, cost=0):
    """
    Products: [(id, amount), (id, amount)...]
    """

    # Create order
    cursor.execute(f"INSERT INTO bd2.zamowienie (koszt, rezerwacja_id) VALUES ({int(cost)}, {reservation_id})")

    cursor.execute(f"SELECT MAX(id) FROM bd2.zamowienie")
    order_id = cursor.fetchall()[0][0]


    # update reservation
    cursor.execute(f"update bd2.rezerwacja set zamowienie_id = {order_id} where id = {reservation_id}")

    # Insert products
    for id, amount in products:
        cursor.execute(f"INSERT INTO bd2.pozycja (liczba, produkt_spozywczy_id, zamowienie_id) VALUES ({amount}, {id}, {order_id})")



    cursor.execute("COMMIT;")

def make_reservation(start, end, room, project, title, cost=0):
    global last_reservation

    # Get id of new reservation
    cursor.execute(f"SELECT MAX(id) FROM bd2.rezerwacja")
    reservation_id = cursor.fetchall()[0][0]
    reservation_id = last_reservation if reservation_id is None else reservation_id + 1
    last_reservation = reservation_id


    sql_str = f"INSERT INTO bd2.rezerwacja (rozpoczecie, zakonczenie, sala_id, cel, projekt_id, koszt)" \
              f" VALUES ('{start}', '{end}', {room}, '{title}', {project}, {int(cost)})"
    cursor.execute(sql_str)


def delete_reservation(reservation_id, with_order=True):
    # Delete reservation
    cursor.execute(f"DELETE FROM bd2.rezerwacja WHERE id = {reservation_id}")

    # Get order id
    if with_order:
        cursor.execute(f"SELECT id FROM bd2.zamowienie WHERE rezerwacja_id = {reservation_id}")
        order_id = cursor.fetchall()[0][0]

        # Delete all products from order
        cursor.execute(f"DELETE FROM bd2.pozycja WHERE zamowienie_id = {order_id}")

        # Delete order
        cursor.execute(f"DELETE FROM bd2.zamowienie WHERE id = {order_id}")

    cursor.execute("COMMIT;")
