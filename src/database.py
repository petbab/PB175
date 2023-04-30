import sqlite3
import re
import hashlib
from typing import Tuple, Optional


class Database:
    __slots__ = "path"

    def __init__(self, path: str):
        self.path = path

    def connect(self) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        con = sqlite3.connect(self.path)
        return con, con.cursor()

    def clear(self):
        con, cur = self.connect()

        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        table_names = [row[0] for row in cur.fetchall()]

        for table_name in table_names:
            cur.execute(f"DELETE FROM {table_name};")
        con.commit()

    def setup(self):
        con, cur = self.connect()

        res = cur.execute('SELECT name FROM sqlite_master')
        tables = [t[0] for t in res.fetchall()]

        if 'customer' not in tables:
            cur.execute('CREATE TABLE customer(email TEXT, password_hash TEXT)')
        if 'order_' not in tables:
            cur.execute('CREATE TABLE order_(status TEXT, time_created INTEGER, customer_id INTEGER)')
        if 'menu_item' not in tables:
            cur.execute('CREATE TABLE menu_item(name TEXT, description TEXT, price INTEGER)')
        con.commit()


class Customer:
    __slots__ = "row_id", "email", "pass_hash"

    def __init__(self, email: str, pass_hash: str, row_id: int = -1) -> None:
        self.row_id, self.email, self.pass_hash = row_id, email, pass_hash

    @classmethod
    def get(cls, db: Database, email: str) -> Optional['Customer']:
        con, cur = db.connect()
        res = cur.execute(f"SELECT *, rowid FROM customer WHERE email = '{email}'").fetchall()
        return cls(*res[0]) if res else None

    def write(self, db: Database) -> None:
        con, cur = db.connect()
        cur.execute(f'INSERT INTO customer VALUES(\'{self.email}\', \'{self.pass_hash}\')')
        con.commit()


def validate_login(email: str, password: str) -> bool:
    if not re.match('^[\w\-.]+@([\w-]+\.)+[\w-]{2,4}$', email) or not password:
        return False

    pass_hash = hashlib.sha256(bytes(password, 'utf-8'),
                               usedforsecurity=True).hexdigest()
    cust = Customer.get(db, email)
    if cust:
        if cust.pass_hash == pass_hash:
            return cust.row_id, True
        return -1, False

    Customer(email, pass_hash).write(db)
    return Customer.get(db, email).row_id, True
