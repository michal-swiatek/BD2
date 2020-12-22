import mysql.connector
import pandas as pd
import numpy as np

import sys

import hashlib

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='1234321',
    database='bd2'
)

my_cursor = mydb.cursor()

users_data = pd.read_csv('data/users.csv')
cities = pd.read_csv('data/cities.csv')
product_categories = pd.read_csv('data/product_categories.csv')
companies_data = pd.read_csv('data/companies.csv')

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

def cities_generator(cursor, data: pd.DataFrame):

    for row in data.iterrows():
        
        city = row[1]['city']

        cursor.execute(f'INSERT INTO miasto (nazwa) VALUES ("{city}")')

    cursor.execute('COMMIT;')

cities_generator(my_cursor, cities)
print("Loaded Cities")

def product_cat_generator(cursor, data: pd.DataFrame):

    for row in data.iterrows():

        categ = row[1]['category']
        cursor.execute(f'INSERT INTO klasyfikacja_produktu (klasa) VALUES ("{categ}")')

    cursor.execute('COMMIT;')

product_cat_generator(my_cursor, product_categories)
print("Loaded product_category")

def users_generator(cursor, data: pd.DataFrame):

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
        work_type = tickets[i]

        # Insert to table depending on the random value
        # TODO: POTENTIALLY LOGINS CAN REPEAT
        cursor.execute(f'INSERT INTO uzytkownik(imie, nazwisko, login, hash_hasla, funkcja) VALUES("{name}", "{surname}", "{login}", "{hash_passwd}", "{work_type}")')
        # cursor.execute(f'SELECT * FROM uzytkownik WHERE imie = {name} AND login = {login}')

        # values = cursor.fetchall()

        # my_cursor.execute(f'INSERT INTO {work_type} (uzytkownik_id) VALUES ("{uzytk_id}")')
    
        # TODO: Update one-hot encoded fields

        # Inserting contacts
        cursor.execute(f'SELECT * FROM uzytkownik WHERE imie = "{name}" AND nazwisko = "{surname}" AND login = "{login}"')

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
        cursor.execute(f'INSERT INTO dane_kontaktowe (kontakt, typ_kontaktu_typ, firma_cateringowa_id, uzytkownik_id) VALUES ("{contact}", "{contact_type}", NULL, "{user_id}")')

        if i % 100 == 0:
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

        cursor.execute(f'INSERT INTO firma_cateringowa(nazwa, limit_zamowien) VALUES ("{company_name}",  "{order_limit}")')



        cursor.execute(f'SELECT * FROM firma_cateringowa WHERE nazwa = "{company_name}" AND limit_zamowien = "{order_limit}"')
        
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
        cursor.execute(f'INSERT INTO dane_kontaktowe (kontakt, typ_kontaktu_typ, firma_cateringowa_id, uzytkownik_id) VALUES ("{contact}", "{contact_type}", "{company_id}", NULL)')


        if i % 100 == 0:
            print(i)

        i += 1

    cursor.execute('COMMIT;')


companies_generator(my_cursor, companies_data)
print("Inserted Companies")



def contact_data_generator(cursor, data: pd.DataFrame):
    
    for row in data:

        row_data = row[1]


        pass






# contact_generator(my_cursor, users_data)
