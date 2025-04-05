from Python.dostop import ustvari_povezavo
import psycopg2


db = 'sem2024_mateov'
host = 'baza.fmf.uni-lj.si'
user = 'javnost'
password = 'javnogeslo'

def dobimo_avte():
    """Returns all cars for registration form"""
    conn, cur = ustvari_povezavo()
    try:
        cur.execute("SELECT id, znamka, model, moc, max_hitrost FROM Avto ORDER BY id")
        cars = cur.fetchall()
        if cars:
            return cars
    finally:
        cur.close()
        conn.close()

    
def prijava_uporabnika(username, password):

    conn, cur = ustvari_povezavo()
    try:
        cur.execute("SELECT * FROM Uporabnik WHERE uporabnisko_ime = %s AND geslo = %s", 
                   (username, password))
        return cur.fetchone() is not None
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def registracija_uporabnika(username=None, ime=None, priimek=None, password=None, avto_id=None):
    """
    - Če so podani podatki, registrira novega uporabnika.
    - Vedno vrne seznam avtomobilov za izbiro.
    """
    conn, cur = ustvari_povezavo()
    
    try:
        # Check if username exists
        cur.execute("SELECT * FROM Uporabnik WHERE uporabnisko_ime = %s", (username,))
        if cur.fetchone():
            return 1
        
        # Check if car exists
        cur.execute("SELECT * FROM Avto WHERE id = %s", (avto_id,))
        if not cur.fetchone():
            return 3
        
        # Get next ID
        cur.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM Uporabnik")
        new_id = cur.fetchone()[0]

        # Insert new user
        cur.execute("""
            INSERT INTO Uporabnik (id, uporabnisko_ime, ime, priimek, geslo, id_avto, tocke)
            VALUES (%s, %s, %s, %s, %s, %s, 0)
        """, (new_id, username, ime, priimek, password, avto_id))
        
        conn.commit()  # THIS WAS MISSING - CRUCIAL!
        return 2
        
    except Exception as e:
        conn.rollback()
        print(f"Database error: {e}")
        return 3
    finally:
        cur.close()
        conn.close()



def prijavi_na_dirko(uporabnik, id_dirke):
    """Prijavi uporabnika na dirko, če izpolnjuje pogoje."""
    conn, cur = ustvari_povezavo()
    try:
        # Preveri, ali je dirka že zaključena
        cur.execute("SELECT COUNT(*) FROM RezultatDirke WHERE id_dirke = %s", (id_dirke,))
        if cur.fetchone()[0] > 0:
            return "❌ Ta dirka je že zaključena! Ne moreš se več prijaviti."

        # Preveri, ali je uporabnik že prijavljen
        cur.execute("""
            SELECT COUNT(*) FROM TrenutnaDirka 
            WHERE id_dirke = %s AND uporabnisko_ime = %s
        """, (id_dirke, uporabnik))
        if cur.fetchone()[0] > 0:
            return "ℹ️ Na to dirko si že prijavljen! Ni potrebno ponovno prijaviti."

        # Preveri, ali je dirka polna
        cur.execute("SELECT COUNT(*) FROM TrenutnaDirka WHERE id_dirke = %s", (id_dirke,))
        if cur.fetchone()[0] >= 20:
            return "❌ Dirka je polna! Poskusi izbrati drugo dirko."

        # Preveri, ali ima uporabnik izbran avto
        cur.execute("SELECT id_avto FROM Uporabnik WHERE uporabnisko_ime = %s", (uporabnik,))
        avto_podatki = cur.fetchone()
        if not avto_podatki or avto_podatki[0] is None:
            return "⚠️ Nimaš izbranega avta! Najprej izberi avto v svojem profilu."

        id_avto = avto_podatki[0]

        # Pridobi model avta
        cur.execute("SELECT model FROM Avto WHERE id = %s", (id_avto,))
        avto_model_podatki = cur.fetchone()
        avto_model = avto_model_podatki[0] if avto_model_podatki else "Neznan model"

        # Vstavi prijavo v TrenutnaDirka
        cur.execute("""
            INSERT INTO TrenutnaDirka (id_dirke, uporabnisko_ime, id_avto, model_avta)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id_dirke, uporabnisko_ime) DO NOTHING
        """, (id_dirke, uporabnik, id_avto, avto_model))

        conn.commit()
        return f"✅ Uspešno si se prijavil na dirko ID: {id_dirke} z avtom {avto_model}!"
    except Exception as e:
        return f"⚠️ Napaka pri prijavi: {e}"
    finally:
        cur.close()
        conn.close()



def pridobi_profil(uporabnik):
    """Vrne podatke o profilu uporabnika."""
    conn, cur = ustvari_povezavo()
    try:
        # Pridobimo osnovne podatke uporabnika
        cur.execute("SELECT ime, priimek, tocke, id_avto FROM Uporabnik WHERE uporabnisko_ime = %s", (uporabnik,))
        rezultat = cur.fetchone()

        if rezultat:
            ime, priimek, tocke, id_avto = rezultat

            # Pridobimo podatke o avtomobilu
            cur.execute("SELECT znamka, model FROM Avto WHERE id = %s", (id_avto,))
            avto_podatki = cur.fetchone()
            avto_ime = f"{avto_podatki[0]} {avto_podatki[1]}" if avto_podatki else "Ni izbran"

            return {
                "uporabnisko_ime": uporabnik,
                "ime": ime,
                "priimek": priimek,
                "tocke": tocke,
                "avto": avto_ime
            }
        else:
            return None  # Če uporabnik ne obstaja

    finally:
        cur.close()
        conn.close()

def spremeni_geslo(uporabnik, novo_geslo):
    """Posodobi geslo uporabnika."""
    conn, cur = ustvari_povezavo()
    try:
        cur.execute("UPDATE Uporabnik SET geslo = %s WHERE uporabnisko_ime = %s", (novo_geslo, uporabnik))
        conn.commit()
        return True
    except Exception as e:
        print(f"Napaka pri spreminjanju gesla: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def spremeni_avto(uporabnik, avto_id):
    """Posodobi avto uporabnika."""
    conn, cur = ustvari_povezavo()
    try:
        cur.execute("UPDATE Uporabnik SET id_avto = %s WHERE uporabnisko_ime = %s", (avto_id, uporabnik))
        conn.commit()
        return True
    except Exception as e:
        print(f"Napaka pri spreminjanju avta: {e}")
        return False
    finally:
        cur.close()
        conn.close()



def moje_dirke(uporabnik):
    conn, cur = ustvari_povezavo()
    try:
        cur.execute("""
            SELECT d.id, d.datum, d.vreme, d.ime_dirkalisca, COUNT(td.uporabnisko_ime) AS prijavljeni
            FROM Dirka d
            JOIN TrenutnaDirka td ON d.id = td.id_dirke
            WHERE td.uporabnisko_ime = %s
            AND d.id NOT IN (SELECT id_dirke FROM RezultatDirke)
            GROUP BY d.id, d.datum, d.vreme, d.ime_dirkalisca       
        """, (uporabnik,))
        vse_dirke = cur.fetchall()

        dirke = []
        for dirka in vse_dirke:
            dirka_podatki = {
                "id": dirka[0],
                "datum": dirka[1],
                "vreme": dirka[2],
                "dirkalisce": dirka[3],
                "prijavljeni": dirka[4],
            }
            dirke.append(dirka_podatki)
            
        return dirke
    except Exception as e:
        print(f"Napaka pri pridobivanju dirk: {e}")  # Log the error for debugging
        return False
    finally:
        cur.close()
        conn.close()

def odjava_dirke(uporabnik, id_dirke):
    conn, cur = ustvari_povezavo()
    try:
        cur.execute("""
            SELECT d.id, d.ime_dirkalisca, d.datum, d.vreme
            FROM Dirka d
            JOIN TrenutnaDirka td ON d.id = td.id_dirke
            WHERE td.uporabnisko_ime = %s
            AND d.id NOT IN (SELECT id_dirke FROM RezultatDirke)
        """, (uporabnik,))
        dirke = cur.fetchall()

        if not dirke:
            return "Nisi prijavljen na nobeno dirko ali pa so rezultati že vneseni."
        
        # Preveri, ali je uporabnik prijavljen na to dirko
        cur.execute("""
            SELECT COUNT(*) FROM TrenutnaDirka 
            WHERE id_dirke = %s AND uporabnisko_ime = %s
        """, (id_dirke, uporabnik))
        if cur.fetchone()[0] == 0:
            return "Nisi prijavljen na to dirko ali rezultati so že vpisani."

        # Odjava iz dirke
        cur.execute("DELETE FROM TrenutnaDirka WHERE id_dirke = %s AND uporabnisko_ime = %s", (id_dirke, uporabnik))
        conn.commit()

        return "✅ Uspešno si se odjavil z dirke!"
    except Exception as e:
        return f"⚠️ Napaka: {e}"
    finally:
        cur.close()
        conn.close()

def kdojekdo(username):
    conn, cur = ustvari_povezavo()
    try:
        cur.execute("SELECT 1 FROM Boss WHERE uporabnisko_ime = %s", (username,))
        return '/meni_admina.html' if cur.fetchone() else '/meni_uporabnika.html'
    finally:
        cur.close()
        conn.close()

