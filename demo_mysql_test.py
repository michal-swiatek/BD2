import mysql.connector
import pandas as pd
import numpy as np

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


contact_type_generator(my_cursor)
print("Inserted Contact Types")


def product_cat_generator(cursor, data: pd.DataFrame):
    for row in data.iterrows():
        categ = row[1]['category']
        cursor.execute(f'INSERT INTO klasyfikacja_produktu (klasa) VALUES ("{categ}")')

    cursor.execute('COMMIT;')


product_cat_generator(my_cursor, product_categories)
print("Loaded product_category")


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


users_generator(my_cursor, users_data)
print("Loaded Users")


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


companies_generator(my_cursor, companies_data)
print("Inserted Companies")


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


buildings_generator(my_cursor, buildings_data)
print('Inserted Buildings')


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


rooms_generator(my_cursor)
print("Inserted Rooms")


def generate_departments(cursor):

    departments = ["Dzial HR",
                   "Dzial Wdrazania",
                   "Dzial Obslugi Klienta",
                   "Dzial Marketingu",
                   "Dzial Cyberbezpieczenstwa",
                   "Dzial IT",
                   "Dzial Ksiegowosci"]

    cursor.execute("SELECT id FROM kierownik")
    managers = [item[0] for item in cursor.fetchall()]

    for dep in departments:
        manager_id = np.random.choice(managers)

        cursor.execute(f'INSERT INTO komorka_organizacyjna(nazwa, kierownik_id) VALUES ("{dep}", {manager_id})')
        managers.remove(manager_id)

    cursor.execute("Commit;")

generate_departments(my_cursor)
print("generated departments")

def update_workers(cursor):

    cursor.execute("SELECT id FROM komorka_organizacyjna")
    department_ids = [item[0] for item in cursor.fetchall()]

    cursor.execute("SELECT id FROM pracownik")
    worker_ids = [item[0] for item in cursor.fetchall()]
    for worker_id in worker_ids:

        dep_id = np.random.choice(department_ids)
        cursor.execute(f"UPDATE pracownik SET komorka_organizacyjna_id = {dep_id} WHERE id = {worker_id}")

    cursor.execute("Commit;")

update_workers(my_cursor)
print("updated workers")