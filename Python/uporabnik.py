from dostop import ustvari_povezavo
import admin

db = 'sem2024_mateov'
host = 'baza.fmf.uni-lj.si'
user = 'javnost'
password = 'javnogeslo'

def prijava_uporabnika(cur):
    while True:
        uporabnik = input("🔑 Vnesi svoje uporabniško ime: ").strip()
        geslo = input("🔒 Vnesi geslo: ").strip()
        
        cur.execute("SELECT * FROM Uporabnik WHERE uporabnisko_ime = %s AND geslo = %s", (uporabnik, geslo))
        rezultat = cur.fetchone()

        if rezultat:
            print(f"\n✅ Prijavljen si kot: {rezultat[3]} {rezultat[4]} (Uporabniško ime: {rezultat[1]})\n")
            return uporabnik
        else:
            print("\n⚠️ Napačno uporabniško ime ali geslo. Poskusi znova.")

def registracija_uporabnika(cur, conn):
    print("\n📌 Registracija novega uporabnika:")

    while True:
        uporabnisko_ime = input("👤 Vnesi uporabniško ime: ").strip()

        cur.execute("SELECT * FROM Uporabnik WHERE uporabnisko_ime = %s", (uporabnisko_ime,))
        if cur.fetchone():
            print("⚠️ To uporabniško ime že obstaja. Izberi drugo.")
        else:
            break
    
    ime = input("📛 Vnesi ime: ").strip()
    priimek = input("📛 Vnesi priimek: ").strip()
    geslo = input("🔒 Ustvari geslo: ").strip()

    cur.execute("SELECT id FROM Avto")
    avtomobili = cur.fetchall()
    
    print("\n🚗 Izberi avto:")
    for avto in avtomobili:
        cur.execute("SELECT znamka, model FROM Avto WHERE id = %s", (avto[0],))
        znamka, model = cur.fetchone()
        print(f"{avto[0]}. {znamka} {model}")

    while True:
        id_avto = input("\n🔢 Vnesi ID izbranega avta: ").strip()
        cur.execute("SELECT * FROM Avto WHERE id = %s", (id_avto,))
        if cur.fetchone():
            break
        else:
            print("⚠️ Neveljaven ID avta. Poskusi znova.")

    cur.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM Uporabnik")
    nov_id = cur.fetchone()[0]

    cur.execute("INSERT INTO Uporabnik (id, uporabnisko_ime, ime, priimek, geslo, id_avto) VALUES (%s, %s, %s, %s, %s, %s)", 
                (nov_id, uporabnisko_ime, ime, priimek, geslo, id_avto))
    
    conn.commit()
    print("\n✅ Registracija uspešna! Zdaj se lahko prijaviš.\n")
    return uporabnisko_ime

def prikazi_meni():
    print("\n📌 GLAVNI MENI:")
    print("1️⃣ Prijava")
    print("2️⃣ Registracija")

def prikazi_meni_uporabnika():
    print("\n📌 MOŽNOSTI:")
    print("1️⃣ Prijava na dirko")
    print("2️⃣ Moj profil")
    print("3️⃣ Odjava")

def prikazi_dirke(cur):
    cur.execute("SELECT id, datum, vreme, ime_dirkalisca FROM Dirka ORDER BY datum")
    dirke = cur.fetchall()

    print("\n🏁 Razpoložljive dirke:")
    for dirka in dirke:
        print(f"➡️ ID: {dirka[0]}, Datum: {dirka[1]}, Vreme: {dirka[2]}, Dirkališče: {dirka[3]}")
    
    return dirke

def izberi_dirko(cur, conn, uporabnik):
    dirke = prikazi_dirke(cur)
    
    izbrani_id = input("\nVnesi ID dirke, na katero se želiš prijaviti: ").strip()

    # Preveri, ali obstaja dirka s tem ID-jem
    cur.execute("SELECT * FROM Dirka WHERE id = %s", (izbrani_id,))
    dirka = cur.fetchone()

    if not dirka:
        print("\n⚠️ Neveljaven ID dirke. Poskusi znova.")
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


def prikazi_profil(cur, conn, uporabnik):
    cur.execute("SELECT ime, priimek, tocke, id_avto FROM Uporabnik WHERE uporabnisko_ime = %s", (uporabnik,))
    rezultat = cur.fetchone()
    if rezultat:
        ime, priimek, tocke, id_avto = rezultat
        cur.execute("SELECT znamka, model FROM Avto WHERE id = %s", (id_avto,))
        avto_podatki = cur.fetchone()
        avto_ime = f"{avto_podatki[0]} {avto_podatki[1]}" if avto_podatki else "Ni izbran"

        print(f"\n👤 Profil: {ime} {priimek}")
        print(f"🚗 Avto: {avto_ime}")
        print(f"🏆 Točke: {tocke}")

        print("\n📌 Uredi profil:")
        print("1️⃣ Spremeni geslo")
        print("2️⃣ Zamenjaj avto")
        print("3️⃣ Nazaj")

        izbira = input("\n🔢 Izberi možnost: ").strip()

        if izbira == "1":
            novo_geslo = input("🔒 Vnesi novo geslo: ").strip()
            cur.execute("UPDATE Uporabnik SET geslo = %s WHERE uporabnisko_ime = %s", (novo_geslo, uporabnik))
            conn.commit()
            print("\n✅ Geslo uspešno spremenjeno!")

        elif izbira == "2":
            cur.execute("SELECT id, znamka, model FROM Avto")
            avtomobili = cur.fetchall()

            print("\n🚗 Izberi nov avto:")
            for avto in avtomobili:
                print(f"{avto[0]}. {avto[1]} {avto[2]}")

            while True:
                nov_avto_id = input("\n🔢 Vnesi ID novega avta: ").strip()
                cur.execute("SELECT * FROM Avto WHERE id = %s", (nov_avto_id,))
                if cur.fetchone():
                    cur.execute("UPDATE Uporabnik SET id_avto = %s WHERE uporabnisko_ime = %s", (nov_avto_id, uporabnik))
                    conn.commit()
                    print("\n✅ Avto uspešno posodobljen!")
                    break
                else:
                    print("⚠️ Neveljaven ID avta. Poskusi znova.")

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
                        izberi_dirko(cur, conn, uporabnik)
                    elif izbira == "2":
                        prikazi_profil(cur, conn, uporabnik)
                    elif izbira == "3":
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

glavna()
