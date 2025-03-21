import psycopg2
import psycopg2.extras

db = 'sem2024_mateov'
host = 'baza.fmf.uni-lj.si'
user = 'javnost'
password = 'javnogeslo'

def ustvari_povezavo():
    conn = psycopg2.connect(
        dbname=db,
        host=host,
        user=user,
        password=password
    )
    return conn