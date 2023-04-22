import sqlite3
import re
import hashlib
from typing import Tuple, Optional


DATABASE = 'data/data.db'


class Customer:
    def __init__(self, row: Tuple[str, str]) -> None:
        self.email, self.pass_hash = row

    @classmethod
    def get(cls, email: str) -> Optional['Customer']:
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        res = cur.execute(f"SELECT * FROM customer WHERE email = '{email}'").fetchall()
        return cls(res[0]) if res else None

    def write(self) -> None:
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        cur.execute(f'INSERT INTO customer VALUES(\'{self.email}\', \'{self.pass_hash}\')')
        con.commit()


def validate_login(email: str, password: str) -> bool:
    if not re.match('^[\w\-.]+@([\w-]+\.)+[\w-]{2,4}$', email) or not password:
        return False

    pass_hash = hashlib.sha256(bytes(password, 'utf-8'),
                               usedforsecurity=True).hexdigest()
    cust = Customer.get(email)
    if cust:
        return cust.pass_hash == pass_hash

    Customer((email, pass_hash)).write()
    return True


def setup():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    res = cur.execute('SELECT name FROM sqlite_master')
    tables = [t[0] for t in res.fetchall()]

    if 'customer' not in tables:
        cur.execute('CREATE TABLE customer(email TEXT, password_hash TEXT)')
    if 'order_' not in tables:
        cur.execute('CREATE TABLE order_(status TEXT, time_created INTEGER, customer_id INTEGER)')
    if 'menu_item' not in tables:
        cur.execute('CREATE TABLE menu_item(name TEXT, description TEXT, price INTEGER)')


def clear():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    for table in ['customer', 'order_', 'menu_item']:
        cur.execute(f'DROP TABLE {table}')
    con.commit()


if __name__ == '__main__':
    clear()
    setup()
else:
    setup()
