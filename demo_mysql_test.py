import mysql.connector
import pandas as pd
import numpy as np
from random import choice, randint, randrange
import datetime
import hashlib

passwd = "1234321"

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password=passwd,
    database='bd2'
)
print("connected!\n")

my_cursor = mydb.cursor()

users_data = pd.read_csv('data/users.csv')
# cities = pd.read_csv('data/cities.csv')
product_categories = pd.read_csv('data/product_categories.csv')
companies_data = pd.read_csv('data/companies.csv')
buildings_data = pd.read_csv('data/buildings.csv')

admins = 160
managers = 40
workers = len(users_data) - admins - managers

tickets = ['adm' for i in range(admins)]
tickets += ['krw' for i in range(managers)]
tickets += ['prc' for i in range(workers)]

tickets = np.array(tickets)

np.random.shuffle(tickets)

print("set up")


def contact_type_generator(cursor):
    my_cursor.execute(f'INSERT INTO typ_kontaktu(typ) VALUES("email")')
    my_cursor.execute(f'INSERT INTO typ_kontaktu(typ) VALUES("nr telefonu")')





def product_cat_generator(cursor, data: pd.DataFrame):
    for row in data.iterrows():
        categ = row[1]['category']
        cursor.execute(f'INSERT INTO klasyfikacja_produktu (klasa) VALUES ("{categ}")')

    cursor.execute('COMMIT;')




def sub_users_generator(cursor, data: pd.DataFrame):
    for idx in range(len(data.index)):
        if tickets[idx] == 'adm':
            cursor.execute(
                f'INSERT INTO administrator(id) VALUES("{idx}")')
        elif tickets[idx] == 'krw':
            cursor.execute(
                f'INSERT INTO kierownik(id) VALUES("{idx}")')
        else:
            cursor.execute(
                f'INSERT INTO pracownik(id) VALUES("{idx}")')


def users_generator(cursor, data: pd.DataFrame):
    sub_users_generator(my_cursor, users_data)
    i = 0

    for row in data.iterrows():

        hasher = hashlib.sha3_224()
        row_data = row[1]

        name = row_data['first_name']
        surname = row_data['last_name']
        login = ''.join(list(np.random.permutation([c for c in name + surname])))[:8]
        password = row_data['password']

        user_phone = row_data['phone']
        user_email = row_data['email']

        hasher.update(bytes(password, encoding='utf-8'))

        hash_passwd = hasher.hexdigest()
        if tickets[i] == 'adm':
            cursor.execute(
                f'INSERT INTO uzytkownik(imie, nazwisko, login, hash_hasla, administrator_id) VALUES("{name}","{surname}", "{login}", "{hash_passwd}", "{i}")')
        elif tickets[i] == 'krw':
            cursor.execute(
                f'INSERT INTO uzytkownik(imie, nazwisko, login, hash_hasla, kierownik_id) VALUES("{name}", "{surname}", "{login}", "{hash_passwd}", "{i}")')
        else:
            cursor.execute(
                f'INSERT INTO uzytkownik(imie, nazwisko, login, hash_hasla, pracownik_id) VALUES("{name}", "{surname}", "{login}", "{hash_passwd}", "{i}")')

        # values = cursor.fetchall()

        # my_cursor.execute(f'INSERT INTO {work_type} (uzytkownik_id) VALUES ("{uzytk_id}")')

        # Inserting contacts
        cursor.execute(
            f'SELECT * FROM uzytkownik WHERE imie = "{name}" AND nazwisko = "{surname}" AND login = "{login}"')

        user_id = cursor.fetchall()[0][0]

        if user_phone is not np.nan:
            contact = user_phone
            cursor.execute('SELECT * FROM typ_kontaktu WHERE typ = "nr telefonu"')
            contact_type = cursor.fetchall()[0][0]
        elif user_email is not np.nan:
            contact = user_email
            cursor.execute('SELECT * FROM typ_kontaktu WHERE typ = "email"')
            contact_type = cursor.fetchall()[0][0]

        # Contact Insertion
        cursor.execute(
            f'INSERT INTO dane_kontaktowe (kontakt, typ_kontaktu_typ, firma_cateringowa_id, uzytkownik_id) VALUES ("{contact}", "{contact_type}", NULL, "{user_id}")')

        if i % 1000 == 0:
            print(i)
        i += 1

    cursor.execute('COMMIT;')





def companies_generator(cursor, data: pd.DataFrame):
    i = 0
    for row in data.iterrows():

        row_data = row[1]
        company_name = row_data['company_name']
        company_phone = row_data['phone']
        company_email = row_data['email']

        order_limit = np.random.randint(50, 100)

        cursor.execute(
            f'INSERT INTO firma_cateringowa(nazwa, limit_zamowien) VALUES ("{company_name}",  "{order_limit}")')

        cursor.execute(
            f'SELECT * FROM firma_cateringowa WHERE nazwa = "{company_name}" AND limit_zamowien = "{order_limit}"')

        extracted_data = cursor.fetchall()

        company_id = extracted_data[0][0]

        if company_phone is not np.nan:
            contact = company_phone
            cursor.execute('SELECT * FROM typ_kontaktu WHERE typ = "nr telefonu"')
            contact_type = cursor.fetchall()[0][0]
        elif company_email is not np.nan:
            contact = company_email
            cursor.execute('SELECT * FROM typ_kontaktu WHERE typ = "email"')
            contact_type = cursor.fetchall()[0][0]

        # Contact Insertion
        cursor.execute(
            f'INSERT INTO dane_kontaktowe (kontakt, typ_kontaktu_typ, firma_cateringowa_id, uzytkownik_id) VALUES ("{contact}", "{contact_type}", "{company_id}", NULL)')

        if i % 100 == 0:
            print(i)

        i += 1

    cursor.execute('COMMIT;')




def buildings_generator(cursor, data):

    inserted_cities = set()
    i = 0
    for row in data.iterrows():

        row_data = row[1]

        name = f'building_{i}'
        post_code = row_data['postcode']
        street = row_data['street']
        number = row_data['number']
        city = row_data['city']


        # cities.add(city)
        if city not in inserted_cities:
            cursor.execute(f'INSERT INTO miasto(nazwa) VALUES ("{city}")')
            inserted_cities.add(city)

        cursor.execute(f'SELECT * FROM miasto WHERE nazwa = "{city}"')

        city_id = cursor.fetchall()[0][0]

        cursor.execute(
            f'INSERT INTO budynek(nazwa, ulica, numer, kod_pocztowy, miasto_id) VALUES ("{name}", "{street}", {number}, "{post_code}", {city_id})')

        if i % 1000 == 0:
            print(i)
        i += 1
    cursor.execute("COMMIT;")





def rooms_generator(cursor):
    num_rooms = 1000
    # Max id budynku
    cursor.execute('SELECT id FROM budynek')
    building_ids = [item[0] for item in cursor.fetchall()]


    for i in range(num_rooms):
        # THINK OF BETTER VALUES THERE
        area = np.random.randint(50, 100)

        room_number = np.random.uniform(5)

        id_bud = np.random.choice(building_ids)

        building_ids.remove(id_bud)

        sitting_places = int(area * 0.4)
        standing_places = int(area * 1.5)

        cursor.execute(
            f"INSERT INTO sala(powierzchnia, numer_sali, budynek_id, miejsca_siedzace, miejsca_stojace) VALUES({area}, {room_number}, {id_bud}, {sitting_places}, {standing_places})")

    cursor.execute('COMMIT;')


def create_departaments(cursor):
    df = pd.read_csv("data/departaments.csv")
    my_cursor.execute("SELECT id FROM kierownik")
    res = [x[0] for x in cursor.fetchall()]
    for i in range(len(df.index)):
        idx = choice(res)
        name = df["depts"][i]
        cursor.execute(f'INSERT INTO komorka_organizacyjna(nazwa, kierownik_id) VALUES("{name}","{idx}")')

    cursor.execute('COMMIT;')
    my_cursor.execute("SELECT id FROM pracownik")
    pracownicy = [x[0] for x in cursor.fetchall()]
    my_cursor.execute("SELECT id FROM komorka_organizacyjna")
    komorki = [x[0] for x in cursor.fetchall()]
    for pracownik in pracownicy:
        k = choice(komorki)
        cursor.execute(f'UPDATE pracownik SET komorka_organizacyjna_id = {k} WHERE id={pracownik}')
    cursor.execute('COMMIT;')


def add_projects(cursor):
    my_cursor.execute("SELECT id FROM komorka_organizacyjna")
    res = [x[0] for x in cursor.fetchall()]
    df = pd.read_csv("data/projects.csv")
    for i in range(len(df.index)):
        name = df["name"][i]
        idx = choice(res)
        cursor.execute(f'INSERT INTO projekt(nazwa, komorka_organizacyjna_id) VALUES("{name}","{idx}")')
    cursor.execute('COMMIT;')


def add_electronics(cursor):
    models = pd.read_csv("data/electro_models.csv")
    upper = max(len(models.index), 200)
    types = pd.read_csv("data/electro_type.csv")
    max_id = len(types.index)
    for i in range(max_id):
        type_i = types["type"][i]
        cursor.execute(f'INSERT INTO rodzaj_sprzetu(rodzaj) VALUE("{type_i}")')

    cursor.execute('COMMIT;')

    cursor.execute("SELECT id FROM rodzaj_sprzetu")
    types_ids = [x[0] for x in cursor.fetchall()]

    for i in range(upper):
        model = models["Model"][i]
        type_id = choice(types_ids)
        cursor.execute(f'INSERT INTO sprzet(model, rodzaj_sprzetu_id) VALUES ("{model}", "{type_id}")')

    cursor.execute('COMMIT;')
    cursor.execute("SELECT id FROM sala")
    sale = [x[0] for x in cursor.fetchall()]

    cursor.execute("SELECT id FROM sprzet")
    electro = [x[0] for x in cursor.fetchall()]

    chosen_pairs = []
    for i in range(upper):

        sala = choice(sale)
        el = choice(electro)
        if (sala, el) in chosen_pairs:

            sala = choice(sale)
            el = choice(electro)


        num = randint(1, 5)
        cursor.execute(f'INSERT INTO dostepnosc_sprzetu(liczba, sala_id, sprzet_id) VALUES ("{num}", "{sala}","{el}")')

        chosen_pairs.append((sala, el))

    cursor.execute('COMMIT;')


def add_misc(cursor):
    df = pd.read_csv("data/produkty.csv")
    names = df["name"]
    prices = df["price"]
    cursor.execute("SELECT id FROM firma_cateringowa")
    companies = [x[0] for x in cursor.fetchall()]
    for k in range(len(df.index)):
        price = prices[k] * 100
        name = names[k]
        comp = choice(companies)
        max_zam = randint(5, 200)

        cursor.execute(f'INSERT INTO produkt_spozywczy(cena, max_zamowienie, firma_cateringowa_id, opis) VALUES("{price}", "{max_zam}", "{comp}", "{name}") ')
    cursor.execute("COMMIT;")

    cursor.execute("SELECT id FROM klasyfikacja_produktu")
    klas = [x[0] for x in cursor.fetchall()]
    cursor.execute("SELECT id FROM produkt_spozywczy")
    prod = [x[0] for x in cursor.fetchall()]
    for p in prod:
        k = choice(klas)
        cursor.execute(f'INSERT INTO przypisanie_produktu(produkt_spozywczy_id, klasyfikacja_produktu_id) VALUES ("{p}","{k}")')
    cursor.execute("COMMIT;")

    obsluga = ["cleaning", "servers", "it support", "cameraperson"]
    for o in obsluga:
        price = randint(1000, 50000)
        cursor.execute(f'INSERT INTO dodatkowa_obsluga(obsluga, cena) VALUES ("{o}", "{price}")')
    cursor.execute("COMMIT;")

    attr = ["wheelchair accesible", "air conditioning"]
    for a in attr:
        cursor.execute(f'INSERT INTO dodatkowy_atrybut(atrybut) VALUE ("{a}")')

    cursor.execute("SELECT id FROM sala")
    sale = [x[0] for x in cursor.fetchall()]
    cursor.execute("SELECT id FROM dodatkowy_atrybut")
    attr = [x[0] for x in cursor.fetchall()]
    i = randint(1, 20)
    for a in range(len(attr)):
        for k in range(30):
            s = sale[i]
            i += 1
            cursor.execute(f'INSERT INTO dostepnosc_atrybutu(sala_id, dodatkowy_atrybut_id) VALUES ("{s}", "{attr[a]}")')

    cursor.execute("COMMIT;")


def insert_reservations(cursor):

    start_date = datetime.date(2019, 10, 12)
    end_date = datetime.date(2021, 3, 12)
    time_between = end_date - start_date
    days_between = time_between.days

    # Get room ids
    cursor.execute('SELECT id FROM sala')
    room_ids = [item[0] for item in cursor.fetchall()]

    # get project ids
    cursor.execute('SELECT id FROM projekt')
    project_ids = [item[0] for item in cursor.fetchall()]

    # better handling taken rooms
    taken_rooms = []

    for i in range(1000):

        random_number = randrange(days_between)
        random_date_start = (start_date + datetime.timedelta(days=random_number)).strftime('%Y-%m-%d %H:%M:%S')
        random_date_end = (start_date + datetime.timedelta(days=randint(1, 3))).strftime('%Y-%m-%d %H:%M:%S')

        room_id = np.random.choice(room_ids)
        if room_id in taken_rooms:
            # print("selecting another room")
            room_id = np.random.choice(room_ids)

        taken_rooms.append(room_id)

        project_id = np.random.choice(project_ids)

        price = 100 * np.random.randint(800, 1000)

        cursor.execute(
            f'INSERT INTO rezerwacja(rozpoczecie, zakonczenie, sala_id, cel, projekt_id, zamowienie_id, koszt) VALUES ("{random_date_start}", "{random_date_end}", {room_id}, "", {project_id}, NULL, {price})')

    cursor.execute('COMMIT;')


def insert_orders(cursor):
    # Get reservations ids

    cursor.execute("SELECT id, koszt FROM rezerwacja")
    res_costs = [item for item in cursor.fetchall()]
    reservation_ids = [item[0] for item in res_costs]
    costs = [item[1] for item in res_costs]



    used_reservations = []
    for i in range(200):

        reservation_id = np.random.choice(reservation_ids)

        if reservation_id not in used_reservations:
            # reservation_id = np.random.choice(reservation_ids)

            index = reservation_ids.index(reservation_id)

            koszt = costs[index]
            used_reservations.append(reservation_id)

            cursor.execute(f"INSERT INTO zamowienie(rezerwacja_id, koszt) VALUES ({reservation_id}, {koszt})")
            cursor.execute('COMMIT;')

            cursor.execute(f'SELECT MAX(id) FROM zamowienie')
            order_id = cursor.fetchall()[0][0]

            cursor.execute(f'UPDATE rezerwacja SET zamowienie_id = {order_id} WHERE id = {reservation_id}')
            cursor.execute("Commit;")



def staff_reservations(cursor):
    # Get reservation ids
    cursor.execute("SELECT id FROM rezerwacja")
    reservation_ids = [item[0] for item in cursor.fetchall()]

    # Get staff ids
    cursor.execute("SELECT id FROM dodatkowa_obsluga")
    staff_ids = [item[0] for item in cursor.fetchall()]

    for r_id in reservation_ids:

        num = np.random.randint(0, 7)
        used_staff = []
        for j in range(num):
            staff_id = np.random.choice(staff_ids)
            if staff_id not in used_staff:
                cursor.execute(
                    f'INSERT INTO rezerwacja_obslugi(dodatkowa_obsluga_id, rezerwacja_id) VALUES ({staff_id}, {r_id})')
                used_staff.append(staff_id)

    cursor.execute('COMMIT;')



def positions_generator(cursor):
    cursor.execute("SELECT id FROM zamowienie")
    order_ids = [item[0] for item in cursor.fetchall()]

    cursor.execute("SELECT id FROM produkt_spozywczy")
    product_ids = [item[0] for item in cursor.fetchall()]

    for ord_id in order_ids:
        num = np.random.randint(7, 17)
        used_products = []
        for j in range(num):
            product_id = np.random.choice(product_ids)
            if product_id not in used_products:
                num_items = np.random.randint(1, 3)
                cursor.execute(
                    f'INSERT INTO pozycja(liczba, produkt_spozywczy_id, zamowienie_id) VALUES ({num_items}, {product_id}, {ord_id})')
                used_products.append(product_id)

    cursor.execute('Commit;')


positions_generator(my_cursor)
print('Inserted positions generator')

contact_type_generator(my_cursor)
print("Inserted Contact Types")

product_cat_generator(my_cursor, product_categories)
print("Loaded product_category")

users_generator(my_cursor, users_data)
print("Loaded Users")

companies_generator(my_cursor, companies_data)
print("Inserted Companies")

buildings_generator(my_cursor, buildings_data)
print('Inserted Buildings')

rooms_generator(my_cursor)
print("Inserted Rooms")

create_departaments(my_cursor)
print("Inserted Departments")
add_projects(my_cursor)
print("Inserted Projects")

add_electronics(my_cursor)
print("Inserted Electronics")
add_misc(my_cursor)
print("Inserted Misc")

insert_reservations(my_cursor)
print('Inserted Reservations')

insert_orders(my_cursor)
print("Inserted orders")

staff_reservations(my_cursor)
print("Inserted staff reservations")

positions_generator(my_cursor)
print("Inserted positions")

mydb.commit()

