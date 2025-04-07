
db = 'sem2024_mateov'
host = 'baza.fmf.uni-lj.si'
user = 'javnost'
password = 'javnogeslo'

import psycopg2
import sqlite3

db = 'sem2024_mateov'
host = 'baza.fmf.uni-lj.si'
user = 'javnost'
password = 'javnogeslo'

def ustvari_povezavo():
    try:
        # Try PostgreSQL (FMF server)
        conn = psycopg2.connect(
            host=host,
            database=db,
            user=user,
            password=password
        )
        cur = conn.cursor()
        return conn, cur
    except:
        # Fallback to SQLite (for Binder)
        conn = sqlite3.connect('backup_baza.db')
        cur = conn.cursor()
        return conn, cur
