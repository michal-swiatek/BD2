import mysql.connector as connector
import hashlib

db = connector.connect(host="localhost", user="root", password="w?Kf+DX2at3Wmroz")
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

cursor.execute(f'INSERT INTO bd2.uzytkownik(imie, nazwisko, login, hash_hasla, administrator_id) VALUES("{"root"}","{"root"}", "{"root"}", "{hashed_password}", "{subtype_id}")')

# Get contact type
cursor.execute(f'SELECT * FROM bd2.typ_kontaktu')
type = cursor.fetchall()[0][0]

# Insert contact
cursor.execute(f'INSERT INTO bd2.dane_kontaktowe (kontakt, typ_kontaktu_typ, firma_cateringowa_id, uzytkownik_id) VALUES ("{"root@root.root"}", "{type}", NULL, "{id}")')

cursor.execute("commit;")

