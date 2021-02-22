import sqlite3
from flask import g
import psycopg2, os

DB_NAME = 'data.db'
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_NAME)
    return db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def create_exchange_rates_table():
    #conn = sqlite3.connect(DB_NAME)
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS rates(date VARCHAR(255), rate REAL, interpolated BOOLEAN)''')
    conn.commit()
    conn.close()


def populate_exchange_rates_table(rates_and_dates_interpolated):
    if len(rates_and_dates_interpolated) < 1:
        print("Incorrect data")
        return
    #conn = sqlite3.connect(DB_NAME)
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO rates VALUES (%s, %s, %s)", rates_and_dates_interpolated)
    conn.commit()
    conn.close()

def get_transaction_sums_for_days(years):
    #conn = sqlite3.connect(DB_NAME)
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    sales_data = cursor.execute(
        "SELECT SUM(sales), orderdate FROM sales GROUP BY orderdate HAVING year_id IN ({seq}) ORDER BY year_id;".format(seq=','.join(['%s']*len(years))), years).fetchall()
    conn.close()
    return sales_data

def get_exchange_rates_for_days(days):
    #conn = sqlite3.connect(DB_NAME)
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    rates = cursor.execute(
        "SELECT rate, interpolated FROM rates GROUP BY date HAVING date IN ({seq}) ORDER BY date;".format(seq=','.join(['%s']*len(days))), days).fetchall()
    conn.close()
    return rates

def check_if_table_exists():
    #conn = sqlite3.connect(DB_NAME)
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    exists = cursor.execute(
        '''SELECT name FROM information_schema.tables table_name='rates';''').fetchone()
    conn.close()
    return exists != None

def drop_exchange_rates_table():
    #conn = sqlite3.connect(DB_NAME)
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        '''DROP TABLE IF EXISTS rates''')
    conn.commit()
    conn.close()
