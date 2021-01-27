import mysql.connector as connector

import hashlib
import string
import random

db = connector.connect(host="localhost", user="root", password="w?Kf+DX2at3Wmroz")
cursor = db.cursor()

logged_as = None

def validate_user(login, password):
    global logged_as

    hasher = hashlib.sha3_224()
    hasher.update(bytes(password.data, encoding='utf-8'))

    cursor.execute(f'SELECT hash_hasla FROM bd2.uzytkownik WHERE login = "{login.data}"')
    db_password = cursor.fetchone()

    valid = db_password == hasher.hexdigest()

    if valid:
        cursor.execute(f'SELECT administrator_id, kierownik_id, pracownik_id FROM bd2.uzytkownik WHERE login = "{login.data}"')
        result = cursor.fetchone()

        if result[0] is not None:
            logged_as = 'a'
        elif result[1] is not None:
            logged_as = 'k'
        elif result[2] is not None:
            logged_as = 'w'

    return valid

def create_account(name, surname, login, mail, role):
    # Generate password and its hash
    letters = string.ascii_lowercase
    password = ''.join(random.choice(letters) for i in range(10))

    hasher = hashlib.sha3_224()
    hasher.update(bytes(password, encoding='utf-8'))

    # Get max_user_id
    cursor.execute(f'SELECT MAX(id) FROM bd2.uzytkownik')
    id = cursor.fetchone()[0]

    # Insert subtype and type
    if role == 'w':
        cursor.execute(f'INSERT INTO bd2.pracownik(id) VALUES("{id}")')

        cursor.execute(f'SELECT MAX(id) FROM bd2.pracownik')
        subtype_id = cursor.fetchone()[0]

        cursor.execute(f'INSERT INTO bd2.uzytkownik(imie, nazwisko, login, hash_hasla, pracownik_id) VALUES("{name}","{surname}", "{login}", "{hasher.hexdigest()}", "{subtype_id}")')
    elif role == 'm':
        cursor.execute(f'INSERT INTO bd2.kierownik(id) VALUES("{id}")')

        cursor.execute(f'SELECT MAX(id) FROM bd2.kierownik')
        subtype_id = cursor.fetchone()[0]

        cursor.execute(f'INSERT INTO bd2.uzytkownik(imie, nazwisko, login, hash_hasla, kierownik_id) VALUES("{name}","{surname}", "{login}", "{hasher.hexdigest()}", "{subtype_id}")')
    elif role == 'a':
        cursor.execute(f'INSERT INTO bd2.administrator(id) VALUES("{id}")')

        cursor.execute(f'SELECT MAX(id) FROM bd2.administrator')
        subtype_id = cursor.fetchone()[0]

        cursor.execute(f'INSERT INTO bd2.uzytkownik(imie, nazwisko, login, hash_hasla, administrator_id) VALUES("{name}","{surname}", "{login}", "{hasher.hexdigest()}", "{subtype_id}")')

    # Get contact type
    cursor.execute(f'SELECT * FROM bd2.typ_kontaktu')
    type = cursor.fetchall()[0][0]

    # Insert contact
    cursor.execute(f'INSERT INTO bd2.dane_kontaktowe (kontakt, typ_kontaktu_typ, firma_cateringowa_id, uzytkownik_id) VALUES ("{mail}", "{type}", NULL, "{id}")')

    cursor.execute("commit;")

    # Return generated password
    return password
