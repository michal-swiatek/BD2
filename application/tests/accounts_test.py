import hashlib
import unittest

import application.accounts as ac
from application import cursor


class MockLogin:
    def __init__(self, data):
        self.data = data


class MyTestCase(unittest.TestCase):
    admin_log = "test_main_admin"
    admin_pass = "123"
    admin_u_id = 0
    admin_id = 0

    man_log = "test_main_man"
    man_pass = 'test_main_man'
    man_u_id = 0
    man_id = 0

    usr_log = "test_main_usr"
    usr_pass = 'test_main_usr'
    usr_u_id = 0
    usr_id = 0

    def adminInit(self):
        hasher = hashlib.sha3_224()
        hasher.update(bytes(self.admin_pass, encoding='utf-8'))
        hash_pass = hasher.hexdigest()

        cursor.execute(f'select max(id) from administrator')
        self.admin_id = cursor.fetchall()[0][0] + 1

        cursor.execute(f'INSERT INTO administrator(id) VALUE({self.admin_id})')
        cursor.execute(
            f'INSERT INTO uzytkownik(imie, nazwisko, login, hash_hasla, administrator_id) VALUES ("test_admin", "test_admin", "{self.admin_log}", "{hash_pass}", "{self.admin_id}") ')
        cursor.execute(f'select id from uzytkownik where administrator_id = {self.admin_id}')
        self.admin_u_id = cursor.fetchall()[0][0]

        cursor.execute(f'INSERT INTO dane_kontaktowe(kontakt, typ_kontaktu_typ,uzytkownik_id) VALUES ("test_admin@test.pl", "email", "{self.admin_u_id}")')

        cursor.execute("commit;")
        lg = MockLogin(self.admin_log)
        ac.db_login(lg)

    def adminCleanUp(self):
        cursor.execute(f'DELETE FROM dane_kontaktowe where uzytkownik_id = {self.admin_u_id}')
        cursor.execute(f'DELETE FROM uzytkownik where administrator_id = {self.admin_id}')
        cursor.execute(f'DELETE FROM administrator where id = {self.admin_id}')
        cursor.execute("commit;")

    def managerInit(self):
        hasher = hashlib.sha3_224()
        hasher.update(bytes(self.man_pass, encoding='utf-8'))
        hash_pass = hasher.hexdigest()

        cursor.execute(f'select max(id) from kierownik')
        self.man_id = cursor.fetchall()[0][0] + 1

        cursor.execute(f'INSERT INTO kierownik(id) VALUE({self.man_id})')
        cursor.execute(
            f'INSERT INTO uzytkownik(imie, nazwisko, login, hash_hasla, kierownik_id) VALUES ("test_man", "test_man", "{self.man_log}", "{hash_pass}", "{self.man_id}") ')
        cursor.execute(f'select id from uzytkownik where kierownik_id = {self.man_id}')
        self.man_u_id = cursor.fetchall()[0][0]

        cursor.execute(
            f'INSERT INTO dane_kontaktowe(kontakt, typ_kontaktu_typ,uzytkownik_id) VALUES ("test_man_main@test.pl", "email", "{self.man_u_id}")')

        cursor.execute("commit;")
        lg = MockLogin(self.man_log)
        ac.db_login(lg)

    def managerCleanUp(self):
        cursor.execute(f'DELETE FROM dane_kontaktowe where uzytkownik_id = {self.man_u_id}')
        cursor.execute(f'DELETE FROM uzytkownik where kierownik_id = {self.man_id}')
        cursor.execute(f'DELETE FROM kierownik where id = {self.man_id}')
        cursor.execute("commit;")

    def userInit(self):
        hasher = hashlib.sha3_224()
        hasher.update(bytes(self.usr_pass, encoding='utf-8'))
        hash_pass = hasher.hexdigest()

        cursor.execute(f'select max(id) from pracownik')
        self.usr_id = cursor.fetchall()[0][0] + 1

        cursor.execute(f'INSERT INTO pracownik(id) VALUE({self.usr_id})')
        cursor.execute(
            f'INSERT INTO uzytkownik(imie, nazwisko, login, hash_hasla, pracownik_id) VALUES ("test_prac", "test_prac", "{self.usr_log}", "{hash_pass}", "{self.usr_id}") ')
        cursor.execute(f'select id from uzytkownik where pracownik_id = {self.usr_id}')
        self.usr_u_id = cursor.fetchall()[0][0]

        cursor.execute(
            f'INSERT INTO dane_kontaktowe(kontakt, typ_kontaktu_typ,uzytkownik_id) VALUES ("test_prac_main@test.pl", "email", "{self.usr_u_id}")')

        cursor.execute("commit;")
        lg = MockLogin(self.usr_log)
        ac.db_login(lg)
        pass

    def userCleanUp(self):
        cursor.execute(f'DELETE FROM dane_kontaktowe where uzytkownik_id = {self.usr_u_id}')
        cursor.execute(f'DELETE FROM uzytkownik where pracownik_id = {self.usr_id}')
        cursor.execute(f'DELETE FROM pracownik where id = {self.usr_id}')
        cursor.execute("commit;")

    def in_test_create_account_worker(self):
        # create user acoount
        cursor.execute(f'select count(*) from uzytkownik')
        prev_u_count = cursor.fetchall()[0][0]
        cursor.execute(f'select count(*) from pracownik')
        prev_w_count = cursor.fetchall()[0][0]

        cursor.execute(f'select min(id) from komorka_organizacyjna')
        dept = cursor.fetchall()[0][0]

        ac.create_account("test_w", "test_w", "test_w", "test_w@test.pl", 'w', dept)

        cursor.execute("COMMIT;")
        cursor.execute(f'select count(*) from uzytkownik')
        aft_u_count = cursor.fetchall()[0][0]
        cursor.execute(f'select count(*) from pracownik')
        aft_w_count = cursor.fetchall()[0][0]
        self.assertEqual(prev_u_count, aft_u_count - 1)
        self.assertEqual(prev_w_count, aft_w_count - 1)

        # get worker id
        cursor.execute('select pracownik_id from uzytkownik where login = "test_w"')
        worker_id = cursor.fetchall()[0][0]
        cursor.execute('select id from uzytkownik where login = "test_w"')
        user_id = cursor.fetchall()[0][0]

        # delete manageraccount
        cursor.execute(f'delete from dane_kontaktowe where uzytkownik_id = {user_id}')
        cursor.execute(f'delete from uzytkownik where pracownik_id = {worker_id}')
        cursor.execute(f'delete from pracownik where id = {worker_id}')
        cursor.execute("commit;")

    def in_test_create_account_manager(self):
        # create user acoount
        cursor.execute(f'select count(*) from uzytkownik')
        prev_u_count = cursor.fetchall()[0][0]
        cursor.execute(f'select count(*) from kierownik')
        prev_m_count = cursor.fetchall()[0][0]

        dept = 1
        ac.create_account("test_m", "test_m", "test_m", "test_m@test.pl", 'm', dept)

        cursor.execute("COMMIT;")
        cursor.execute(f'select count(*) from uzytkownik')
        aft_u_count = cursor.fetchall()[0][0]
        cursor.execute(f'select count(*) from kierownik')
        aft_m_count = cursor.fetchall()[0][0]
        self.assertEqual(prev_u_count, aft_u_count - 1)
        self.assertEqual(prev_m_count, aft_m_count - 1)

        # get kierownik_id
        cursor.execute('select kierownik_id from uzytkownik where login = "test_m"')
        manager_id = cursor.fetchall()[0][0]
        cursor.execute('select id from uzytkownik where login = "test_m"')
        user_id = cursor.fetchall()[0][0]

        # delete manager account
        cursor.execute(f'delete from dane_kontaktowe where uzytkownik_id = {user_id}')
        cursor.execute(f'delete from uzytkownik where id={user_id}')
        cursor.execute(f'delete from kierownik where id={manager_id}')
        cursor.execute("commit;")

    def in_test_create_admin(self):
        # get ids
        cursor.execute(f'select count(*) from uzytkownik')
        prev_u_count = cursor.fetchall()[0][0]
        cursor.execute(f'select count(*) from administrator')
        prev_a_count = cursor.fetchall()[0][0]

        dept = 1
        ac.create_account("test_A", "test_A", "test_A", "test_A@test.pl", 'a', dept)

        cursor.execute("COMMIT;")
        cursor.execute(f'select count(*) from uzytkownik')
        aft_u_count = cursor.fetchall()[0][0]
        cursor.execute(f'select count(*) from administrator')
        aft_a_count = cursor.fetchall()[0][0]
        self.assertEqual(prev_u_count, aft_u_count - 1)
        self.assertEqual(prev_a_count, aft_a_count - 1)

        # get admin_id
        cursor.execute('select administrator_id from uzytkownik where login = "test_A"')
        test_a_id = cursor.fetchall()[0][0]
        cursor.execute('select id from uzytkownik where login = "test_A"')
        user_id = cursor.fetchall()[0][0]

        # delete admin account
        cursor.execute(f'delete from dane_kontaktowe where uzytkownik_id = {user_id}')
        cursor.execute(f'delete from uzytkownik where id={user_id}')
        cursor.execute(f'delete from kierownik where id={test_a_id}')
        cursor.execute("commit;")

    def test_create_account(self):
        self.adminInit()
        self.in_test_create_account_worker()
        self.in_test_create_account_manager()
        self.in_test_create_admin()
        self.adminCleanUp()

    def test_change_password(self):
        self.adminInit()
        newpassword = "kindarandompassword"
        ac.change_password(newpassword)
        hasher = hashlib.sha3_224()
        hasher.update(bytes(str(newpassword), encoding='utf-8'))
        hashed_password = hasher.hexdigest()

        cursor.execute(f'SELECT hash_hasla from uzytkownik where id={self.admin_u_id}')
        hash_in_db = cursor.fetchall()[0][0]

        self.assertEqual(hashed_password, hash_in_db)

        self.adminCleanUp()

    def test_edit_account(self):
        self.adminInit()
        new_name = "test_new_name"
        new_surname = "test_new_surname"
        new_login = "test_new_login"
        new_mail = "test_new_mail"
        ac.edit_account(new_name, new_surname, new_login, new_mail)

        cursor.execute(
            f'SELECT kontakt from dane_kontaktowe where uzytkownik_id={self.admin_u_id}')
        temp = cursor.fetchall()
        db_mail = temp[0][0]

        cursor.execute(f'SELECT imie, nazwisko, login from uzytkownik where id={self.admin_u_id}')
        res = cursor.fetchone()
        db_name = res[0]
        db_surname = res[1]
        db_login = res[2]
        self.assertEqual(db_name, new_name)
        self.assertEqual(db_surname, new_surname)
        self.assertEqual(db_mail, new_mail)
        self.assertEqual(db_login, new_login)
        self.adminCleanUp()

    def test_delete_account_admin(self):
        self.adminInit()
        cursor.execute('SELECT count(*) from uzytkownik')
        num_us_before = cursor.fetchone()[0]

        ac.delete_account()

        cursor.execute('SELECT count(*) from uzytkownik')
        num_us_after = cursor.fetchone()[0]

        self.assertEqual(num_us_after+1, num_us_before)

    def test_delete_account_manager(self):
        self.managerInit()
        cursor.execute('SELECT count(*) from uzytkownik')
        num_us_before = cursor.fetchone()[0]

        ac.delete_account()

        cursor.execute('SELECT count(*) from uzytkownik')
        num_us_after = cursor.fetchone()[0]

        self.assertEqual(num_us_after+1, num_us_before)

    def test_delete_account_user(self):
        self.userInit()
        cursor.execute('SELECT count(*) from uzytkownik')
        num_us_before = cursor.fetchone()[0]

        ac.delete_account()

        cursor.execute('SELECT count(*) from uzytkownik')
        num_us_after = cursor.fetchone()[0]

        self.assertEqual(num_us_after+1, num_us_before)

    def test_create_account_when_not_admin(self):
        self.userInit()

        # create user acoount
        cursor.execute(f'select count(*) from uzytkownik')
        prev_u_count = cursor.fetchall()[0][0]
        cursor.execute(f'select count(*) from pracownik')
        prev_w_count = cursor.fetchall()[0][0]

        cursor.execute(f'select min(id) from komorka_organizacyjna')
        dept = cursor.fetchall()[0][0]

        ac.create_account("test_w", "test_w", "test_w", "test_w@test.pl", 'w', dept)

        cursor.execute("COMMIT;")
        cursor.execute(f'select count(*) from uzytkownik')
        aft_u_count = cursor.fetchall()[0][0]
        cursor.execute(f'select count(*) from pracownik')
        aft_w_count = cursor.fetchall()[0][0]
        self.assertEqual(prev_u_count, aft_u_count)
        self.assertEqual(prev_w_count, aft_w_count)

        self.userCleanUp()


if __name__ == '__main__':
    unittest.main()
