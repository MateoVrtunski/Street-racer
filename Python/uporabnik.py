from dostop import ustvari_povezavo
import admin
import psycopg2
from bottle import template


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


def prikazi_meni():
    print("\n📌 GLAVNI MENI:")
    print("1️⃣ Prijava")
    print("2️⃣ Registracija")


def prikazi_meni_uporabnika():
    print("\n📌 MOŽNOSTI:")
    print("1️⃣ Rezultati dirk")
    print("2️⃣ Poglej Championship")
    print("3️⃣ Prijava na dirko")
    print("4️⃣ Odjava na dirko")
    print("5️⃣ Moj profil")
    print("6️⃣ Odjava")


def izberi_dirko(cur, conn, uporabnik):
    dirke = admin.prikazi_trenutno_dirko(cur)
    
    izbrani_id = input("\nVnesi ID dirke, na katero se želiš prijaviti (ali 0 za nazaj): ").strip()
    if izbrani_id == "0":
        print("🔙 Vračam te nazaj v meni.")
        return False

    # Preveri, ali obstaja dirka s tem ID-jem
    cur.execute("SELECT * FROM Dirka WHERE id = %s", (izbrani_id,))
    dirka = cur.fetchone()

    if not dirka:
        print("\n⚠️ Neveljaven ID dirke. Poskusi znova.")
        return False
    
    cur.execute("SELECT COUNT(*) FROM RezultatDirke WHERE id_dirke = %s", (izbrani_id,))
    rezultati_obstajajo = cur.fetchone()[0] > 0

    if rezultati_obstajajo:
        print("\n❌ Ta dirka je že zaključena! Ne moreš se več prijaviti.")
        return False

    cur.execute("""
        SELECT COUNT(*) FROM TrenutnaDirka 
        WHERE id_dirke = %s AND uporabnisko_ime = %s
    """, (izbrani_id, uporabnik))
    ze_prijavljen = cur.fetchone()[0] > 0

    if ze_prijavljen:
        print("\nℹ️ Na to dirko si že prijavljen! Ni potrebno ponovno prijaviti.")
        return False
    
    # Preveri, koliko ljudi je že prijavljenih na to dirko
    cur.execute("SELECT COUNT(*) FROM TrenutnaDirka WHERE id_dirke = %s", (izbrani_id,))
    stevilo_prijavljenih = cur.fetchone()[0]

    if stevilo_prijavljenih >= 20:
        print("\n❌ Dirka je polna! Poskusi izbrati drugo dirko.")
        return False

    # Pridobi podatke o uporabnikovem avtu
    cur.execute("SELECT id_avto FROM Uporabnik WHERE uporabnisko_ime = %s", (uporabnik,))
    avto_podatki = cur.fetchone()

    if not avto_podatki or avto_podatki[0] is None:
        print("\n⚠️ Nimaš izbranega avta! Najprej izberi avto v svojem profilu.")
        return False

    id_avto = avto_podatki[0]

    # Pridobi model avta
    cur.execute("SELECT model FROM Avto WHERE id = %s", (id_avto,))
    avto_model_podatki = cur.fetchone()
    avto_model = avto_model_podatki[0] if avto_model_podatki else "Neznan model"

    # Vstavi prijavo v TrenutnaDirka, če še ni prijavljen
    cur.execute("""
        INSERT INTO TrenutnaDirka (id_dirke, uporabnisko_ime, id_avto, model_avta)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id_dirke, uporabnisko_ime) DO NOTHING
    """, (izbrani_id, uporabnik, id_avto, avto_model))

    conn.commit()
    print(f"\n✅ Uspešno si se prijavil na dirko ID: {izbrani_id} z avtom {avto_model}!")
    return True


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

def odjava_dirke(cur, conn, uporabnik):
    # Prikaži dirke, kjer je uporabnik prijavljen in rezultati še niso vpisani
    cur.execute("""
        SELECT d.id, d.ime_dirkalisca, d.datum
        FROM Dirka d
        JOIN TrenutnaDirka td ON d.id = td.id_dirke
        WHERE td.uporabnisko_ime = %s
        AND d.id NOT IN (SELECT id_dirke FROM RezultatDirke)
    """, (uporabnik,))
    dirke = cur.fetchall()

    if not dirke:
        print("\nℹ️ Nisi prijavljen na nobeno dirko ali pa so rezultati že vneseni.")
        return

    print("\n🚗 Dirke, s katerih se lahko odjaviš:")
    for dirka in dirke:
        print(f"📅 ID: {dirka[0]}, Dirka: {dirka[1]}, Datum: {dirka[2]}")

    while True:
        izbrani_id = input("\nVnesi ID dirke, s katere se želiš odjaviti (ali 0 za nazaj): ").strip()
        if izbrani_id == "0":
            print("🔙 Vračam te nazaj v meni.")
            return

        # Preveri, ali je uporabnik prijavljen na to dirko
        cur.execute("""
            SELECT COUNT(*) FROM TrenutnaDirka 
            WHERE id_dirke = %s AND uporabnisko_ime = %s
        """, (izbrani_id, uporabnik))
        if cur.fetchone()[0] == 0:
            print("\n⚠️ Nisi prijavljen na to dirko ali rezultati so že vpisani.")
            continue

        # Odjava iz dirke
        cur.execute("DELETE FROM TrenutnaDirka WHERE id_dirke = %s AND uporabnisko_ime = %s", (izbrani_id, uporabnik))
        conn.commit()
        print("\n✅ Uspešno si se odjavil z dirke!")
        return


def glavna():
    conn, cur = ustvari_povezavo()

    while True:
        print("\n🔹 Izberi način prijave:")
        print("1️⃣ Uporabnik")
        print("2️⃣ Admin")
        print("3️⃣ Izhod")
        izbira = input("\n🔢 Izberi možnost: ").strip()

        if izbira == "1":
            while True:
                prikazi_meni()
                izbira = input("\n🔢 Izberi možnost: ").strip()
                if izbira == "1":
                    uporabnik = prijava_uporabnika(cur)
                elif izbira == "2":
                    uporabnik = registracija_uporabnika(cur, conn)
                else:
                    print("⚠️ Neveljavna izbira. Poskusi znova.")
                    continue

                while True:
                    prikazi_meni_uporabnika()
                    izbira = input("\n🔢 Izberi možnost: ").strip()
                    if izbira == "1":
                        admin.prikazi_rezultate_dirke(cur)
                    elif izbira == "2":
                        admin.poglej_championship(cur)
                    elif izbira == "3":
                        izberi_dirko(cur, conn, uporabnik)
                    elif izbira == "4":
                        odjava_dirke(cur, conn, uporabnik)
                    elif izbira == "5":
                        prikazi_profil(cur, conn, uporabnik)
                    elif izbira == "6":
                        print("\n👋 Odjava...")
                        break
                    else:
                        print("⚠️ Neveljavna izbira. Poskusi znova.")
                break

        elif izbira == "2":
            admin.admin_menu(cur, conn)

        elif izbira == "3":
            print("\n👋 Izhod iz programa...")
            break

        else:
            print("⚠️ Neveljavna izbira. Poskusi znova.")


