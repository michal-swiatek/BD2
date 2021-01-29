import hashlib
import string
import random

from application import cursor

logged_as = None


def set_inits():
    global logged_as, logged_role

    logged_role = None
    logged_as = None


def get_logged_username():
    global logged_as
    return logged_as


def db_login(login):
    global logged_as, logged_role

    db_logout()

    cursor.execute(
        f'SELECT administrator_id, kierownik_id, pracownik_id FROM bd2.uzytkownik WHERE login = "{login.data}"')
    result = cursor.fetchall()[0]

    logged_as = login.data

    if result[0] is not None:
        logged_role = 'a'
    elif result[1] is not None:
        logged_role = 'm'
    elif result[2] is not None:
        logged_role = 'w'


def db_logout():
    global logged_as, logged_role

    logged_as = None
    logged_role = None


def validate_user(login, password):
    hasher = hashlib.sha3_224()
    hasher.update(bytes(password.data, encoding='utf-8'))

    cursor.execute(f'SELECT hash_hasla FROM bd2.uzytkownik WHERE login = "{login.data}"')

    temp = cursor.fetchall()
    if len(temp) == 0:
        return False

    db_password = temp[0][0]

    return db_password == hasher.hexdigest()


def generate_password(length):
    # Generate password and its hash
    letters = string.ascii_lowercase
    password = ''.join(random.choice(letters) for i in range(length))

    return password


def create_account(name, surname, login, mail, role, department):
    if logged_role == 'a':
        password = generate_password(10)

        hasher = hashlib.sha3_224()
        hasher.update(bytes(str(password), encoding='utf-8'))
        hashed_password = hasher.hexdigest()

        if department is None:
            department = 0

        # Get max_user_id
        cursor.execute(f'SELECT MAX(id) FROM bd2.uzytkownik')
        user_id = cursor.fetchall()[0][0] + 1

        # Insert subtype and type
        if role == 'w':
            cursor.execute(
                f'INSERT INTO bd2.pracownik (id, komorka_organizacyjna_id) VALUES("{user_id}", {department})')

            cursor.execute(
                f'INSERT INTO bd2.uzytkownik(imie, nazwisko, login, hash_hasla, pracownik_id) VALUES("{name}","{surname}", "{login}", "{hashed_password}", "{user_id}")')

            cursor.execute(f'SELECT MAX(id) FROM bd2.pracownik')
            subtype_id = cursor.fetchall()[0][0]

            cursor.execute(f'SELECT id from uzytkownik where pracownik_id = {user_id}')
            user_id = cursor.fetchall()[0][0]

        elif role == 'm':
            cursor.execute(f'INSERT INTO bd2.kierownik(id) VALUES("{user_id}")')

            cursor.execute(
                f'INSERT INTO bd2.uzytkownik(imie, nazwisko, login, hash_hasla, kierownik_id) VALUES("{name}","{surname}", "{login}", "{hashed_password}", "{user_id}")')
            cursor.execute(f'SELECT id from uzytkownik where kierownik_id = {user_id}')
            user_id = cursor.fetchall()[0][0]
        elif role == 'a':
            cursor.execute(f'INSERT INTO bd2.administrator(id) VALUES("{user_id}")')

            cursor.execute(
                f'INSERT INTO bd2.uzytkownik(imie, nazwisko, login, hash_hasla, administrator_id) VALUES("{name}","{surname}", "{login}", "{hashed_password}", "{user_id}")')

            cursor.execute(f'SELECT id from uzytkownik where administrator_id = {user_id}')
            user_id = cursor.fetchall()[0][0]

        # Get contact type
        cursor.execute(f'SELECT * FROM bd2.typ_kontaktu')
        type = cursor.fetchall()[0][0]

        # Insert contact
        cursor.execute(
            f'INSERT INTO bd2.dane_kontaktowe (kontakt, typ_kontaktu_typ, uzytkownik_id) VALUES ("{mail}", "{type}","{user_id}")')

        cursor.execute("commit;")

        # Return generated password
        return password
    else:
        return None


def edit_account(name, surname, login, mail):
    if logged_as is not None:
        # Update users table
        cursor.execute(f'SELECT id FROM bd2.uzytkownik WHERE login="{logged_as}"')
        id = cursor.fetchall()[0][0]
        cursor.execute(
            f'UPDATE bd2.uzytkownik SET imie="{name}", nazwisko="{surname}", login="{login}" WHERE id="{id}"')

        # Update contacts table
        cursor.execute(f'SELECT * FROM bd2.typ_kontaktu')
        type = cursor.fetchall()[0][0]

        cursor.execute(f'UPDATE bd2.dane_kontaktowe SET kontakt="{mail}", typ_kontaktu_typ="{type}" WHERE uzytkownik_id="{id}"')

        cursor.execute("commit;")


def change_password(password):
    if logged_as is not None:
        hasher = hashlib.sha3_224()
        hasher.update(bytes(str(password), encoding='utf-8'))
        hashed_password = hasher.hexdigest()

        cursor.execute(f'UPDATE bd2.uzytkownik SET hash_hasla="{hashed_password}"')
        cursor.execute("commit;")


def delete_account(account_login=None):
    global logged_role

    if account_login is not None and logged_role != 'a':
        return

    if account_login is None:
        account_login = logged_as

    if account_login is not None:

        # get user id
        cursor.execute(f'SELECT id FROM bd2.uzytkownik WHERE login="{account_login}"')
        id = cursor.fetchall()[0][0]

        # Delete subtype record
        print(logged_role)
        if logged_role == 'a':
            cursor.execute(
                f'SELECT administrator_id FROM bd2.uzytkownik WHERE  bd2.uzytkownik.id={id}')
        elif logged_role == 'm':
            cursor.execute(
                f'SELECT kierownik_id FROM bd2.uzytkownik WHERE bd2.uzytkownik.id={id}')
        elif logged_role == 'w':
            cursor.execute(
                f'SELECT pracownik_id FROM bd2.uzytkownik WHERE  bd2.uzytkownik.id={id}')

        id_sub = cursor.fetchall()[0][0]

        # del contact data
        cursor.execute(f'DELETE FROM bd2.dane_kontaktowe WHERE uzytkownik_id={id}')

        # delete user
        cursor.execute(f'DELETE FROM bd2.uzytkownik WHERE id="{id}"')

        # delete subtype
        if logged_role == 'a':
            cursor.execute(f'DELETE FROM bd2.administrator WHERE id="{id_sub}"')
        elif logged_role == 'm':
            cursor.execute(f'DELETE FROM bd2.kierownik WHERE id="{id_sub}"')
        elif logged_role == 'w':
            cursor.execute(f'DELETE FROM bd2.pracownik WHERE id="{id_sub}"')

        cursor.execute("commit;")

        db_logout()
