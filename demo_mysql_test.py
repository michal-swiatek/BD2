import mysql.connector
import pandas as pd
import numpy as np
from random import choice, randint
import hashlib

passwd = "w?Kf+DX2at3Wmroz"

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

    for i in range(upper):
        sala = choice(sale)
        num = randint(1, 5)
        el = choice(electro)
        cursor.execute(f'INSERT INTO dostepnosc_sprzetu(liczba, sala_id, sprzet_id) VALUES ("{num}", "{sala}","{el}")')

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


mydb.commit()

