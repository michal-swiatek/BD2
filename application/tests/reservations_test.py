import unittest
from application import cursor
from application import reservations
import datetime
import application.accounts as ac
import hashlib







class TestReservations(unittest.TestCase):

    def create_mock_reservation(self) -> int:
        cursor.execute(
            "INSERT INTO bd2.rezerwacja (rozpoczecie, zakonczenie, sala_id, cel, projekt_id, koszt, zamowienie_id)"
            " VALUES ('2022-10-10 12:30:00', '2020-10-10 14:30:00', 1, '_testDelete', 1, 1000, NULL);")
        cursor.execute("select max(id) from bd2.rezerwacja")
        last_id = cursor.fetchall()[0][0]

        return last_id

    def remove_mock_reservation(self, r_id):
        cursor.execute(f'delete from bd2.rezerwacja where id={r_id}')
        cursor.execute('commit;')


    def test_make_reservation_no_order(self):
        cursor.execute(f'select count(*) from bd2.rezerwacja')
        before_n_reservations = cursor.fetchall()[0][0]
        start, end = '2022-10-10 12:30:00', '2020-10-10 14:30:00'
        room, project, title, cost = 1, 1, '_test Market analysis2', 1000

        reservations.make_reservation(start, end, room, project, title, cost)
        cursor.execute(f'select count(*) from bd2.rezerwacja')
        after_n_reservations = cursor.fetchall()[0][0]

        self.assertEqual(before_n_reservations, after_n_reservations - 1, 'a row was inserted')

        # check if correct data was inserted
        cursor.execute('select max(id) from bd2.rezerwacja')
        last_id = cursor.fetchall()[0][0]
        cursor.execute(f'select rozpoczecie, cel, koszt, zamowienie_id from bd2.rezerwacja where id = {last_id}')
        new_reservation = cursor.fetchall()[0]
        self.assertEqual(new_reservation[0], datetime.datetime.strptime(start, '%Y-%m-%d %H:%M:%S'))
        self.assertEqual(new_reservation[1], title)
        self.assertEqual(new_reservation[2], cost)
        self.assertEqual(new_reservation[3], None)

        # clean up
        cursor.execute(f'delete from bd2.rezerwacja where id={last_id}')
        cursor.execute('commit;')

    def test_create_order(self):
        products = [(1, 2), (2, 10), (3, 40)]
        cost = 2137

        # make mock reservation
        mock_id = self.create_mock_reservation()

        cursor.execute('select count(*) from bd2.zamowienie')
        before_n_orders = cursor.fetchall()[0][0]

        reservations.create_order(products, cost, mock_id)

        # check if a new row was inserted
        cursor.execute('select count(*) from bd2.zamowienie')
        after_n_orders = cursor.fetchall()[0][0]
        self.assertEqual(before_n_orders, after_n_orders - 1)

        # clean up
        cursor.execute('select max(id) from bd2.zamowienie')
        id = cursor.fetchall()[0][0]
        cursor.execute(f'update bd2.rezerwacja set zamowienie_id = NULL where zamowienie_id = {id}')
        cursor.execute(f'delete from bd2.zamowienie where id={id}')
        self.remove_mock_reservation(mock_id)

    def test_delete_reservation(self):


        cursor.execute("INSERT INTO bd2.rezerwacja (rozpoczecie, zakonczenie, sala_id, cel, projekt_id, koszt, zamowienie_id)"
                       " VALUES ('2022-10-10 12:30:00', '2020-10-10 14:30:00', 1, '_testDelete', 1, 1000, NULL);")

        cursor.execute('select max(id) from bd2.rezerwacja')
        last_id = cursor.fetchall()[0][0]

        cursor.execute(f'select count(*) from bd2.rezerwacja')
        before_n_reservations = cursor.fetchall()[0][0]

        reservations.delete_reservation(last_id, with_order=False)


        cursor.execute(f'select count(*) from bd2.rezerwacja')
        after_n_reservations = cursor.fetchall()[0][0]

        self.assertEqual(before_n_reservations, after_n_reservations + 1, 'a row was deleted')
        cursor.execute(f'select id from bd2.rezerwacja where id = {last_id}')
        result = cursor.fetchall()
        self.assertTrue(len(result) == 0, 'correct row was deleted')















if __name__ == '__main__':
    unittest.main()
