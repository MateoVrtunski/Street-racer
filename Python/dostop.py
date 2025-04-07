import os 
db = 'sem2024_mateov'
host = 'baza.fmf.uni-lj.si'
user = 'javnost'
password = 'javnogeslo'



DB_PORT = os.environ.get('POSTGRES_PORT', 5432)
def ustvari_povezavo():
    import psycopg2
    conn = psycopg2.connect(
        host=host,
        database=db,  # zamenjaj s pravim imenom baze
        user=user,  # zamenjaj s pravim uporabnikom
        password=password,
        port = DB_PORT  # zamenjaj s pravim geslom
    )
    cur = conn.cursor()  # Ustvari kurzor za izvajanje poizvedb
    return conn, cur