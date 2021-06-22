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
            " VALUES ('2022-10-10 12:30:00', '2020-10-10 14:30:00', 1, '_testDelete', 1, 0, NULL);")
        cursor.execute("select max(id) from bd2.rezerwacja")
        last_id = cursor.fetchall()[0][0]

        return last_id

    def remove_mock_reservation(self, r_id):
        cursor.execute(f'delete from bd2.rezerwacja where id={r_id}')
        cursor.execute('commit;')

    def get_cost(self, products):
        cost = 0
        for p_id, p_count in products:
            cursor.execute(f'select cena from produkt_spozywczy where id={p_id}')
            p_cost = cursor.fetchall()[0][0]
            cost += p_cost * p_count
        return cost

    def test_make_reservation_no_order(self):
        cursor.execute(f'select count(*) from bd2.rezerwacja')
        before_n_reservations = cursor.fetchall()[0][0]
        start, end = '2022-10-10 12:30:00', '2020-10-10 14:30:00'
        room, project, title = 1, 1, '_test Market analysis2'

        reservations.make_reservation(start, end, room, project, title)
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
        self.assertEqual(new_reservation[2], 0)  # cost of a reservation with no order is 0
        self.assertEqual(new_reservation[3], None)

        # clean up
        cursor.execute(f'delete from bd2.rezerwacja where id={last_id}')
        cursor.execute('commit;')

    def test_create_order(self):
        prod_ids = [1, 2, 3]
        prod_amounts = [2, 10, 40]
        products = list(zip(prod_ids, prod_amounts))

        # make mock reservation
        reservation_id = self.create_mock_reservation()

        cursor.execute('select count(*) from bd2.zamowienie')
        before_n_orders = cursor.fetchall()[0][0]

        reservations.create_order(products, reservation_id)

        # check if a new row was inserted
        cursor.execute('select count(*) from bd2.zamowienie')
        after_n_orders = cursor.fetchall()[0][0]
        self.assertEqual(before_n_orders, after_n_orders - 1)

        # check if the correct order data was inserted
        cursor.execute('select max(id) from bd2.zamowienie')
        result = cursor.fetchall()
        self.assertTrue(len(result) != 0)
        order_id = result[0][0]
        cursor.execute(f'select koszt from bd2.zamowienie where id = {order_id}')
        cost_inserted = cursor.fetchall()[0][0]
        self.assertEqual(cost_inserted, self.get_cost(products),
                         'denormalization trigger calculates the order cost correctly')

        cursor.execute(f'select koszt from bd2.rezerwacja where id={reservation_id}')
        reserv_cost = cursor.fetchall()[0][0]
        self.assertEqual(reserv_cost, self.get_cost(products),
                         'denormalization trigger calculates the reservation cost correctly')

        cursor.execute(f'select produkt_spozywczy_id, liczba from pozycja where zamowienie_id ={order_id}')
        result = cursor.fetchall()
        self.assertListEqual(result, products, 'correct products were inserted into the order')

        # clean up
        cursor.execute('select max(id) from bd2.zamowienie')
        id = cursor.fetchall()[0][0]
        cursor.execute(f'update bd2.rezerwacja set zamowienie_id = NULL where zamowienie_id = {id}')
        cursor.execute(f'delete from bd2.zamowienie where id={id}')
        self.remove_mock_reservation(reservation_id)

    def test_delete_reservation(self):
        cursor.execute(
            "INSERT INTO bd2.rezerwacja (rozpoczecie, zakonczenie, sala_id, cel, projekt_id, koszt, zamowienie_id)"
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
        self.assertTrue(len(result) == 0, 'the correct row was deleted')


if __name__ == '__main__':
    unittest.main()
