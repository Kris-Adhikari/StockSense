import sqlite3
from datetime import datetime

class Database:
    @staticmethod
    def connect():
        return sqlite3.connect('stocks.db')

    @staticmethod
    def setup():
        conn = Database.connect()
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS portfolio
                    (user_id TEXT,
                     ticker TEXT,
                     shares REAL,
                     buy_price REAL,
                     PRIMARY KEY (user_id, ticker))''')
        c.execute('''CREATE TABLE IF NOT EXISTS portfolio_history
                    (user_id TEXT,
                     date TEXT,
                     total_value REAL,
                     PRIMARY KEY (user_id, date))''')
        conn.commit()
        conn.close()

    @staticmethod
    def add_stock(user_id, ticker, shares, price):
        conn = Database.connect()
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO portfolio VALUES (?, ?, ?, ?)',
                 (user_id, ticker, shares, price))
        conn.commit()
        conn.close()

    @staticmethod
    def get_portfolio(user_id):
        conn = Database.connect()
        c = conn.cursor()
        c.execute('SELECT ticker, shares, buy_price FROM portfolio WHERE user_id = ?',
                 (user_id,))
        stocks = c.fetchall()
        conn.close()
        return stocks

    @staticmethod
    def remove_stock(user_id, ticker):
        conn = Database.connect()
        c = conn.cursor()
        c.execute('DELETE FROM portfolio WHERE user_id = ? AND ticker = ?',
                 (user_id, ticker))
        deleted = c.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

    @staticmethod
    def update_portfolio_history(user_id, total_value):
        conn = Database.connect()
        c = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        c.execute('INSERT OR REPLACE INTO portfolio_history VALUES (?, ?, ?)',
                 (user_id, today, total_value))
        conn.commit()
        conn.close()

    @staticmethod
    def get_last_two_values(user_id):
        conn = Database.connect()
        c = conn.cursor()
        c.execute('''SELECT total_value FROM portfolio_history 
                    WHERE user_id = ? 
                    ORDER BY date DESC LIMIT 2''', (user_id,))
        values = c.fetchall()
        conn.close()
        return values
