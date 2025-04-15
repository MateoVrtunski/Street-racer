from Python.dostop import ustvari_povezavo
import psycopg2
import bcrypt

#Tukaj so vse funkcije potrebne za delovanje aplikacije kot uporabnik

def dobimo_avte():
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
        cur.execute("SELECT geslo FROM Uporabnik WHERE uporabnisko_ime = %s", (username,))
        row = cur.fetchone()
        if not row:
            return False

        hashed_password = row[0] 

        geslo_bytes = password.encode('utf-8')
        return bcrypt.checkpw(geslo_bytes, hashed_password.encode('utf-8'))

    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        cur.close()
        conn.close()


def registracija_uporabnika(username=None, ime=None, priimek=None, password=None, avto_id=None):
    
    conn, cur = ustvari_povezavo()
    
    try:
        cur.execute("SELECT * FROM Uporabnik WHERE uporabnisko_ime = %s", (username,))
        if cur.fetchone():
            return 1  
        
        cur.execute("SELECT * FROM Avto WHERE id = %s", (avto_id,))
        if not cur.fetchone():
            return 3 
       
        cur.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM Uporabnik")
        new_id = cur.fetchone()[0]

        cur.execute("SELECT model FROM Avto WHERE id = %s", (avto_id,))
        result = cur.fetchone()
        if not result:
            print(f"Napaka: Avto z ID {avto_id} ne obstaja")
            return False
        model_avta = result[0]

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_str = hashed.decode('utf-8')  

        cur.execute("""
            INSERT INTO Uporabnik (id, uporabnisko_ime, ime, priimek, geslo, id_avto, model_avta, tocke)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 0)
        """, (new_id, username, ime, priimek, hashed_str, avto_id, model_avta))

        conn.commit()
        return 2 

    except Exception as e:
        conn.rollback()
        print(f"Database error: {e}")
        return 3  
    finally:
        cur.close()
        conn.close()

def prijavi_na_dirko(uporabnik, id_dirke=None):

    conn, cur = ustvari_povezavo()
    try:
        if id_dirke == None:
            return "Izberite dirko!"
        
        cur.execute("SELECT COUNT(*) FROM RezultatDirke WHERE id_dirke = %s", (id_dirke,))
        if cur.fetchone()[0] > 0:
            return "❌ Ta dirka je že zaključena! Ne moreš se več prijaviti."

        
        cur.execute("""
            SELECT COUNT(*) FROM TrenutnaDirka 
            WHERE id_dirke = %s AND uporabnisko_ime = %s
        """, (id_dirke, uporabnik))
        if cur.fetchone()[0] > 0:
            return "ℹ️ Na to dirko si že prijavljen! Ni potrebno ponovno prijaviti."

        
        cur.execute("SELECT COUNT(*) FROM TrenutnaDirka WHERE id_dirke = %s", (id_dirke,))
        if cur.fetchone()[0] >= 20:
            return "❌ Dirka je polna! Poskusi izbrati drugo dirko."

        
        cur.execute("SELECT id_avto FROM Uporabnik WHERE uporabnisko_ime = %s", (uporabnik,))
        avto_podatki = cur.fetchone()
        if not avto_podatki or avto_podatki[0] is None:
            return "⚠️ Nimaš izbranega avta! Najprej izberi avto v svojem profilu."

        id_avto = avto_podatki[0]

        
        cur.execute("SELECT model FROM Avto WHERE id = %s", (id_avto,))
        avto_model_podatki = cur.fetchone()
        avto_model = avto_model_podatki[0] if avto_model_podatki else "Neznan model"

        
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
    conn, cur = ustvari_povezavo()
    try:
       
        cur.execute("SELECT ime, priimek, tocke, id_avto FROM Uporabnik WHERE uporabnisko_ime = %s", (uporabnik,))
        rezultat = cur.fetchone()

        if rezultat:
            ime, priimek, tocke, id_avto = rezultat

            
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
            return None  

    finally:
        cur.close()
        conn.close()

def spremeni_geslo(uporabnik, novo_geslo):

    conn, cur = ustvari_povezavo()
    try:
        hashed = bcrypt.hashpw(novo_geslo.encode('utf-8'), bcrypt.gensalt())
        hashed_str = hashed.decode('utf-8')
        cur.execute("UPDATE Uporabnik SET geslo = %s WHERE uporabnisko_ime = %s", (hashed_str, uporabnik))
        conn.commit()
        return True
    except Exception as e:
        print(f"Napaka pri spreminjanju gesla: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def spremeni_avto(uporabnik, avto_id):

    conn, cur = ustvari_povezavo()
    try:
        cur.execute("SELECT model FROM Avto WHERE id = %s", (avto_id,))
        result = cur.fetchone()
        
        if not result:
            print(f"Napaka: Avto z ID {avto_id} ne obstaja")
            return False
            
        model_avta = result[0]
        cur.execute("UPDATE Uporabnik SET id_avto = %s, model_avta = %s WHERE uporabnisko_ime = %s", (avto_id, model_avta, uporabnik))
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

def odjava_dirke(uporabnik, id_dirke=None):
    conn, cur = ustvari_povezavo()
    try:
        if id_dirke == None:
            return "Izberite dirko!"

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
        return 'meni_admina.html' if cur.fetchone() else 'meni_uporabnika.html'
    finally:
        cur.close()
        conn.close()

