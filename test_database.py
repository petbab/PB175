import os
import unittest
import database as db

DATABASE = 'tests.db'


def set_up_database():
    database = db.Database(DATABASE)
    database.clear()
    database.setup()


class TestLogin(unittest.TestCase):
    def setUp(self) -> None:
        set_up_database()

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(DATABASE)

    def test_login(self):
        """ This test focuses on the `login` function from `database.py`. """
        # connect to database
        database = db.Database(DATABASE)
        _, cur = database.connect()

        # tests invalid email and password
        self.assertFalse(db.login(database, '', '')[1])
        self.assertFalse(db.login(database, 'my@mail.com', '')[1])
        self.assertFalse(db.login(database, 'not.a.mail.com', '123')[1])
        self.assertFalse(db.login(database, 'almost@mail', '123')[1])
        self.assertFalse(db.login(database, 'not@a@mail', '123')[1])

        # make sure database is empty
        res = cur.execute('SELECT * FROM customer').fetchall()
        self.assertEqual(0, len(res))

        # tests valid email and password
        row_id, valid = db.login(database, 'valid@mail.com', 'password')
        self.assertTrue(valid)
        self.assertEqual(1, row_id)
        row_id, valid = db.login(database, 'new.valid999@mail.com', '123')
        self.assertTrue(valid)
        self.assertEqual(2, row_id)

        # login attempt to an existing account with the wrong password
        self.assertFalse(db.login(database, 'valid@mail.com', 'bad_password')[1])

        # login attempt to an existing account with the correct password
        row_id, valid = db.login(database, 'valid@mail.com', 'password')
        self.assertTrue(valid)
        self.assertEqual(1, row_id)

        # check that two accounts were created
        res = cur.execute('SELECT * FROM customer').fetchall()
        self.assertEqual(2, len(res))


class TestCustomer(unittest.TestCase):
    def setUp(self) -> None:
        set_up_database()

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(DATABASE)

    def test_get(self):
        """ This test focuses on the `get` method in `Customer`. """
        # connect to database
        database = db.Database(DATABASE)
        con, cur = database.connect()

        # get on a nonexistent customer should return None
        self.assertIsNone(db.Customer.get(database, 'not.mail.com'))

        # create a customer
        mail, pass_hash = 'some@mail.com', 'pass_hash'
        cur.execute(f'INSERT INTO customer VALUES(\'{mail}\', \'{pass_hash}\')')
        con.commit()

        # check that it exists and has the right attributes
        cust = db.Customer.get(database, mail)
        self.assertIsNotNone(cust)
        self.assertEqual(mail, cust.email)
        self.assertEqual(pass_hash, cust.pass_hash)
        self.assertEqual(1, cust.row_id)

    def test_write(self):
        """ This test focuses on the `write` method in `Customer`. """
        # connect to database
        database = db.Database(DATABASE)
        _, cur = database.connect()

        # make sure database is empty
        res = cur.execute('SELECT * FROM customer').fetchall()
        self.assertEqual(0, len(res))

        # create 20 customers and write them into the database
        accounts = [(f'mail{i}', f'hash{i}') for i in range(20)]
        for mail, pass_hash in accounts:
            db.Customer(mail, pass_hash).write(database)

        # make sure they're there
        res = cur.execute("SELECT * FROM customer").fetchall()
        self.assertEqual(20, len(res))

        # check the data
        for i in range(20):
            self.assertEqual(accounts[i], res[i])


if __name__ == '__main__':
    unittest.main()
