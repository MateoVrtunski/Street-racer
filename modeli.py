from dostop import ustvari_povezavo
import psycopg2.extras

def prijava(uporabnisko_ime):
    conn = ustvari_povezavo()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM Uporabnik WHERE uporabnisko_ime = %s", (uporabnisko_ime,))
    uporabnik = cur.fetchone()
    conn.close()
    return uporabnik

def seznam_dirkalisca():
    conn = ustvari_povezavo()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM Dirkalisce")
    dirkalisca = cur.fetchall()
    conn.close()
    return dirkalisca

def seznam_dirk():
    conn = ustvari_povezavo()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM Dirka")
    dirke = cur.fetchall()
    conn.close()
    return dirke

def seznam_uporabnikov():
    conn = ustvari_povezavo()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM Uporabnik")
    uporabniki = cur.fetchall()
    conn.close()
    return uporabniki

def dodaj_rezultat(id_dirke, uporabnisko_ime, uvrstitev, tocke):
    conn = ustvari_povezavo()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO RezultatDirke (id_dirke, uporabnisko_ime, uvrstitev, tocke)
        VALUES (%s, %s, %s, %s)
    """, (id_dirke, uporabnisko_ime, uvrstitev, tocke))

    cur.execute("""
        UPDATE Uporabnik SET tocke = tocke + %s
        WHERE uporabnisko_ime = %s
    """, (tocke, uporabnisko_ime))

    conn.commit()
    conn.close()