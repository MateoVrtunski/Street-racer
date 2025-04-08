import psycopg2
from Python.dostop import ustvari_povezavo

#Tukaj so vse funkcije, ki so potrebne, ko se vpišemo kot admin.

def prijava_admina(username, password):

    conn, cur = ustvari_povezavo()
    try:
        cur.execute("SELECT * FROM Boss WHERE uporabnisko_ime = %s AND geslo = %s", 
                   (username, password))
        return cur.fetchone() is not None
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def dodaj_admina(uporabnisko_ime):
    conn, cur = ustvari_povezavo()
    try:
        
        cur.execute("SELECT * FROM Uporabnik WHERE uporabnisko_ime = %s", (uporabnisko_ime,))
        uporabnik = cur.fetchone()

        
        cur.execute("SELECT * FROM Boss WHERE uporabnisko_ime = %s", (uporabnisko_ime,))
        admin_ze_obstaja = cur.fetchone()

        cur.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM Uporabnik")
        nov_id = cur.fetchone()[0]

        if not uporabnik:
            return "⚠️ Uporabnik s tem imenom ne obstaja."
        elif admin_ze_obstaja:
            return "⚠️ Ta uporabnik je že admin."
        else:
            cur.execute(
                "INSERT INTO Boss (id, uporabnisko_ime, geslo, ime, priimek) "
                "VALUES (%s, %s, %s, %s, %s)",
                (nov_id, uporabnik[1], uporabnik[2], uporabnik[3], uporabnik[4])
            )
            cur.execute("DELETE FROM Uporabnik WHERE uporabnisko_ime = %s", (uporabnisko_ime,))

            conn.commit()
            return f"✅ Uporabnik {uporabnisko_ime} je zdaj admin!"
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def prikazi_trenutno_dirko():
    conn, cur = ustvari_povezavo()
    
    try:
       
        cur.execute("""
            SELECT d.id, d.datum, d.vreme, d.ime_dirkalisca, COUNT(td.uporabnisko_ime) AS prijavljeni
            FROM Dirka d
            LEFT JOIN TrenutnaDirka td ON d.id = td.id_dirke
            GROUP BY d.id, d.datum, d.vreme, d.ime_dirkalisca
            ORDER BY d.id
        """)
        vse_dirke = cur.fetchall()

       
        cur.execute("""
            SELECT id_dirke
            FROM RezultatDirke
            WHERE tocke > 0
            GROUP BY id_dirke
            HAVING COUNT(*) >= 10
        """)
        koncane_dirke_ids = {dirka[0] for dirka in cur.fetchall()}  

        dirke = []
        koncane_dirke = []

        for dirka in vse_dirke:
            dirka_podatki = {
                "id": dirka[0],
                "datum": dirka[1],
                "vreme": dirka[2],
                "dirkalisce": dirka[3],
                "prijavljeni": dirka[4],  
                "max_prijav": 20  
            }

            if dirka[0] in koncane_dirke_ids:
                koncane_dirke.append(dirka_podatki)
            else:
                dirke.append(dirka_podatki)

        return dirke, koncane_dirke

    finally:
        cur.close()
        conn.close()

def mozne_dirke():
    conn, cur = ustvari_povezavo()
    
    try:
        
        cur.execute("""
            SELECT d.id, d.datum, d.vreme, d.ime_dirkalisca, COUNT(td.uporabnisko_ime) AS prijavljeni
            FROM Dirka d
            LEFT JOIN TrenutnaDirka td ON d.id = td.id_dirke
            WHERE d.id NOT IN (SELECT DISTINCT id_dirke FROM RezultatDirke)
            GROUP BY d.id, d.datum, d.vreme, d.ime_dirkalisca
            HAVING COUNT(td.uporabnisko_ime) >= 10
            ORDER BY d.id
        """)
        vse_dirke = cur.fetchall()

        dirke = []

        for dirka in vse_dirke:
            dirka_podatki = {
                "id": dirka[0],
                "datum": dirka[1],
                "vreme": dirka[2],
                "dirkalisce": dirka[3],
                "prijavljeni": dirka[4], 
                "max_prijav": 20  
            }
            dirke.append(dirka_podatki)
            
        return dirke

    finally:
        cur.close()
        conn.close()

def prijavljeni_na_dirko(id_dirke):
    conn, cur = ustvari_povezavo()
    try:
        
        cur.execute("SELECT * FROM Dirka WHERE id = %s", (id_dirke,))
        if not cur.fetchone():
            return "⚠️ Neveljaven ID dirke."

        
        cur.execute("SELECT COUNT(*) FROM RezultatDirke WHERE id_dirke = %s AND tocke > 0", (id_dirke,))
        if cur.fetchone()[0] >= 10:
            return "❌ Ta dirka je že zaključena!"

        
        cur.execute("SELECT uporabnisko_ime FROM TrenutnaDirka WHERE id_dirke = %s", (id_dirke,))
        prijavljeni = [row[0] for row in cur.fetchall()]

        if not prijavljeni:
            return "⚠️ Ni prijavljenih uporabnikov za to dirko."
        if len(prijavljeni) < 10:
            return "⚠️ Premalo tekmovalcev za točkovanje!"
        
        cur.execute("SELECT uporabnisko_ime FROM TrenutnaDirka WHERE id_dirke = %s", (id_dirke,))
        prijavljeni = cur.fetchall()
        return prijavljeni
    
    except Exception as e:
        print(f"Napaka pri spreminjanju gesla: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def doloci_rezultate(id_dirke, rezultat_seznam):
    conn, cur = ustvari_povezavo()
    try:
        if id_dirke == None:
            return "Izberite dirko!"
        
        cur.execute("SELECT * FROM Dirka WHERE id = %s", (id_dirke,))
        if not cur.fetchone():
            return "⚠️ Neveljaven ID dirke."

        
        cur.execute("SELECT COUNT(*) FROM RezultatDirke WHERE id_dirke = %s AND tocke > 0", (id_dirke,))
        if cur.fetchone()[0] >= 10:
            return "❌ Ta dirka je že zaključena!"

        
        cur.execute("SELECT uporabnisko_ime FROM TrenutnaDirka WHERE id_dirke = %s", (id_dirke,))
        prijavljeni = [row[0] for row in cur.fetchall()]

        if not prijavljeni:
            return "⚠️ Ni prijavljenih uporabnikov za to dirko."
        if len(prijavljeni) < 10:
            return "⚠️ Premalo tekmovalcev za točkovanje!"
        
        cur.execute("SELECT uporabnisko_ime FROM TrenutnaDirka WHERE id_dirke = %s", (id_dirke,))
        prijavljeni = [row[0] for row in cur.fetchall()]
       
        tocke_f1 = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1] + [0] * (len(prijavljeni) - 10)

        for i, uporabnik in enumerate(rezultat_seznam):
            if uporabnik not in prijavljeni:
                return f"⚠️ Uporabnik '{uporabnik}' ni prijavljen na dirko!"

            cur.execute("""
                INSERT INTO RezultatDirke (id_dirke, uporabnisko_ime, uvrstitev, tocke)
                VALUES (%s, %s, %s, %s)
            """, (id_dirke, uporabnik, i+1, tocke_f1[i]))

            cur.execute("""
                UPDATE Uporabnik SET tocke = tocke + %s WHERE uporabnisko_ime = %s
            """, (tocke_f1[i], uporabnik))

        conn.commit()
        return "✅ Rezultati uspešno shranjeni!"
    
    except Exception as e:
        print(f"Napaka pri spreminjanju gesla: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def pridobi_profil_admina(uporabnik):
    """Vrne podatke o profilu uporabnika."""
    conn, cur = ustvari_povezavo()
    try:
        
        cur.execute("SELECT ime, priimek FROM Boss WHERE uporabnisko_ime = %s", (uporabnik,))
        rezultat = cur.fetchone()

        if rezultat:
            ime, priimek = rezultat
            return {
                "uporabnisko_ime": uporabnik,
                "ime": ime,
                "priimek": priimek
            }
        else:
            return None  

    finally:
        cur.close()
        conn.close()

def spremeni_geslo_admina(uporabnik, novo_geslo):
    """Posodobi geslo uporabnika."""
    conn, cur = ustvari_povezavo()
    try:
        cur.execute("UPDATE Boss SET geslo = %s WHERE uporabnisko_ime = %s", (novo_geslo, uporabnik))
        conn.commit()
        return True
    except Exception as e:
        print(f"Napaka pri spreminjanju gesla: {e}")
        return False
    finally:
        cur.close()
        conn.close()
        
def pridobi_rezultate_dirk():
    """Vrne seznam preteklih dirk z rezultati."""
    conn, cur = ustvari_povezavo()
    try:
        
        cur.execute("""
            SELECT DISTINCT d.id, d.datum, d.ime_dirkalisca
            FROM Dirka d
            JOIN RezultatDirke r ON d.id = r.id_dirke
            ORDER BY d.datum DESC
        """)
        dirke = cur.fetchall()

        dirka_podatki = []
        for dirka in dirke:
            id_dirke, datum, ime_dirkalisca = dirka

            
            cur.execute("""
                SELECT r.uvrstitev, r.uporabnisko_ime, r.tocke
                FROM RezultatDirke r
                WHERE r.id_dirke = %s
                ORDER BY r.uvrstitev ASC
            """, (id_dirke,))
            rezultati = cur.fetchall()

            dirka_podatki.append({
                "id": id_dirke,
                "datum": datum,
                "ime_dirkalisca": ime_dirkalisca,
                "rezultati": [
                    {"uvrstitev": r[0], "uporabnisko_ime": r[1], "tocke": r[2]}
                    for r in rezultati
                ]
            })
        
        return dirka_podatki

    finally:
        cur.close()
        conn.close()

def poglej_championship():
    """Vrne trenutno stanje championshipa kot seznam slovarjev."""
    conn, cur = ustvari_povezavo()
    try:
        cur.execute("SELECT ime, priimek, tocke FROM Uporabnik ORDER BY tocke DESC")
        rezultat = cur.fetchall()
        
        championship = []
        for i, vrstica in enumerate(rezultat, start=1):
            championship.append({
                "mesto": i,
                "ime": vrstica[0],
                "priimek": vrstica[1],
                "tocke": vrstica[2]
            })
        
        return championship
    finally:
        cur.close()
        conn.close()



