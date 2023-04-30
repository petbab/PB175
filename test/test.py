import unittest
import src.database as db
import os


class TestDatabase(unittest.TestCase):
    data_path = 'test.db'

    def setUp(self) -> None:
        db.Database(TestDatabase.data_path).clear()

    @classmethod
    def setUpClass(cls) -> None:
        data = db.Database(cls.data_path)
        data.setup()

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove(cls.data_path)

    def test_validate_login(self):
        """ This test focuses on the `validate_login` function from `database.py`. """

        # database setup
        data = db.Database(TestDatabase.data_path)
        con, cur = data.connect()

        # make sure database is empty
        res = cur.execute('SELECT * FROM customer').fetchall()
        self.assertEqual(0, len(res))

        # test invalid email and password
        self.assertFalse(db.login(data, '', '')[1])
        self.assertFalse(db.login(data, 'my@mail.com', '')[1])
        self.assertFalse(db.login(data, 'not.a.mail.com', '123')[1])
        self.assertFalse(db.login(data, 'almost@mail', '123')[1])
        self.assertFalse(db.login(data, 'not@a@mail', '123')[1])

        # make sure database is empty
        res = cur.execute('SELECT * FROM customer').fetchall()
        self.assertEqual(0, len(res))

        # test valid email and password
        row_id, valid = db.login(data, 'valid@mail.com', 'password')
        self.assertTrue(valid)
        self.assertEqual(1, row_id)
        row_id, valid = db.login(data, 'new.valid999@mail.com', '123')
        self.assertTrue(valid)
        self.assertEqual(2, row_id)

        # login attempt to an existing account with the wrong password
        self.assertFalse(db.login(data, 'valid@mail.com', 'bad_password')[1])

        # login attempt to an existing account with the correct password
        row_id, valid = db.login(data, 'valid@mail.com', 'password')
        self.assertTrue(valid)
        self.assertEqual(1, row_id)

        # check that two accounts were created
        res = cur.execute('SELECT * FROM customer').fetchall()
        self.assertEqual(2, len(res))

    def test_customer(self):
        """ This test focuses on the `Customer` class from `database.py`. """

        # database setup
        data = db.Database(TestDatabase.data_path)
        con, cur = data.connect()

    def test_order(self):
        """ This test focuses on the `Order` class from `database.py`. """


if __name__ == '__main__':
    unittest.main()
