import os 
db = 'sem2024_mateov'
host = 'baza.fmf.uni-lj.si'
user = 'javnost'
password = 'javnogeslo'

#povezava do baze

DB_PORT = os.environ.get('POSTGRES_PORT', 5432)
def ustvari_povezavo():
    import psycopg2
    conn = psycopg2.connect(
        host=host,
        database=db,  
        user=user,  
        password=password,
        port = DB_PORT  
    )
    cur = conn.cursor() 
    return conn, cur