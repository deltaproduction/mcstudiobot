import sqlite3

from config import DATABASE as db_path


class Database:
    def __init__(self):
        self.path = db_path
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()

    def create_user(self, user_id, username):
        query = f"INSERT INTO users(user_id, username) VALUES ({user_id}, '{username}')"
        self.cursor.execute(query)
        self.connection.commit()

    def is_registered(self, user_id):
        query = f"SELECT * FROM users WHERE user_id={user_id}"
        return bool(len(self.cursor.execute(query).fetchall()))

    def get_user_expenses(self, user_id):
        query = f"SELECT * FROM expenses WHERE user_id={user_id}"
        result = self.cursor.execute(query).fetchall()
        return [i[-1] for i in result]

    def get_user_income(self, user_id):
        query = f"SELECT * FROM income WHERE user_id={user_id}"
        result = self.cursor.execute(query).fetchall()
        return [i[-1] for i in result]

    def get_user_balance(self, user_id):
        income = sum(self.get_user_income(user_id))
        expenses = sum(self.get_user_expenses(user_id))
        result = income - expenses
        return result

    def add_user_income(self, user_id, *count):
        for i in count:
            query = f"INSERT INTO income(user_id, count) VALUES ({user_id}, '{i}')"
            self.cursor.execute(query)

        self.connection.commit()

    def add_user_expenses(self, user_id, *count):
        for i in count:
            query = f"INSERT INTO expenses(user_id, count) VALUES ({user_id}, '{i}')"
            self.cursor.execute(query)

        self.connection.commit()
