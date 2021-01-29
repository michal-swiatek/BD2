import mysql.connector as connector
import hashlib

db = connector.connect(host="localhost", user="root", password="1234321")
cursor = db.cursor()

password = "root"

hasher = hashlib.sha3_224()
hasher.update(bytes(str(password), encoding='utf-8'))
hashed_password = hasher.hexdigest()

# Get max_user_id
cursor.execute(f'SELECT MAX(id) FROM bd2.uzytkownik')
id = cursor.fetchall()[0][0]

# Insert subtype and type

cursor.execute(f'INSERT INTO bd2.administrator(id) VALUES("{id}")')

cursor.execute(f'SELECT MAX(id) FROM bd2.administrator')
subtype_id = cursor.fetchall()[0][0]

cursor.execute(f'INSERT INTO bd2.uzytkownik(imie, nazwisko, login, hash_hasla, administrator_id) VALUES("{"root"}","{"root"}", "{"root_admin"}", "{hashed_password}", "{subtype_id}")')

# Get contact type
cursor.execute(f'SELECT * FROM bd2.typ_kontaktu')
type = cursor.fetchall()[0][0]

# Insert contact
cursor.execute(f'INSERT INTO bd2.dane_kontaktowe (kontakt, typ_kontaktu_typ, firma_cateringowa_id, uzytkownik_id) VALUES ("{"root_admin@root.root"}", "{type}", NULL, "{id}")')

cursor.execute("commit;")


### root_worker

# Get max_user_id
cursor.execute(f'SELECT MAX(id) FROM bd2.uzytkownik')
id = cursor.fetchall()[0][0]

cursor.execute(f'INSERT INTO bd2.pracownik(id) VALUES("{id}")')

cursor.execute(f'SELECT MAX(id) FROM bd2.pracownik')
subtype_id = cursor.fetchall()[0][0]

cursor.execute(f'INSERT INTO bd2.uzytkownik(imie, nazwisko, login, hash_hasla, pracownik_id) VALUES("{"root"}","{"root"}", "{"root_worker"}", "{hashed_password}", "{subtype_id}")')

# Get contact type
cursor.execute(f'SELECT * FROM bd2.typ_kontaktu')
type = cursor.fetchall()[0][0]

# Insert contact
cursor.execute(f'INSERT INTO bd2.dane_kontaktowe (kontakt, typ_kontaktu_typ, firma_cateringowa_id, uzytkownik_id) VALUES ("{"root_worker@root.root"}", "{type}", NULL, "{id}")')

cursor.execute("commit;")

### root_manager

# Get max_user_id
cursor.execute(f'SELECT MAX(id) FROM bd2.uzytkownik')
id = cursor.fetchall()[0][0]

cursor.execute(f'INSERT INTO bd2.kierownik(id) VALUES("{id}")')

cursor.execute(f'SELECT MAX(id) FROM bd2.kierownik')
subtype_id = cursor.fetchall()[0][0]

cursor.execute(f'INSERT INTO bd2.uzytkownik(imie, nazwisko, login, hash_hasla, kierownik_id) VALUES("{"root"}","{"root"}", "{"root_manager"}", "{hashed_password}", "{subtype_id}")')

# Get contact type
cursor.execute(f'SELECT * FROM bd2.typ_kontaktu')
type = cursor.fetchall()[0][0]

# Insert contact
cursor.execute(f'INSERT INTO bd2.dane_kontaktowe (kontakt, typ_kontaktu_typ, firma_cateringowa_id, uzytkownik_id) VALUES ("{"root_manager@root.root"}", "{type}", NULL, "{id}")')

cursor.execute("commit;")