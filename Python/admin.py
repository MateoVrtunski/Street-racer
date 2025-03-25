import psycopg2

def prijava_admin(cur):
    print("\n🔑 ADMIN PRIJAVA")
    uporabnisko_ime = input("Vnesi uporabniško ime admina: ").strip()
    geslo = input("Vnesi geslo: ").strip()

    cur.execute("SELECT * FROM Boss WHERE uporabnisko_ime = %s AND geslo = %s", (uporabnisko_ime, geslo))
    admin = cur.fetchone()

    if admin:
        print(f"\n✅ Prijava uspešna! Pozdravljen, {admin[3]} {admin[4]}.")
        return admin[1]  # Vrnemo uporabniško ime
    else:
        print("\n❌ Napačno uporabniško ime ali geslo.")
        return None

def dodaj_admina(cur, conn):
    uporabnisko_ime = input("🔹 Vnesi uporabniško ime uporabnika, ki ga želiš dodati kot admina: ").strip()

    # Preverimo, ali uporabnik obstaja
    cur.execute("SELECT * FROM Uporabnik WHERE uporabnisko_ime = %s", (uporabnisko_ime,))
    uporabnik = cur.fetchone()

    # Preverimo, ali je že admin
    cur.execute("SELECT * FROM Boss WHERE uporabnisko_ime = %s", (uporabnisko_ime,))
    admin_ze_obstaja = cur.fetchone()

    cur.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM Uporabnik")
    nov_id = cur.fetchone()[0]

    if not uporabnik:
        print("⚠️ Uporabnik s tem imenom ne obstaja.")
    elif admin_ze_obstaja:
        print("⚠️ Ta uporabnik je že admin.")
    else:
        cur.execute(
            "INSERT INTO Boss (id, uporabnisko_ime, geslo, ime, priimek) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (nov_id, uporabnik[1], uporabnik[2], uporabnik[3], uporabnik[4])
        )
        conn.commit()
        print(f"✅ Uporabnik {uporabnisko_ime} je zdaj admin!")


def prikazi_trenutno_dirko(cur):
    cur.execute("""
        SELECT d.id, d.datum, d.ime_dirkalisca, COUNT(td.uporabnisko_ime) 
        FROM Dirka d
        LEFT JOIN TrenutnaDirka td ON d.id = td.id_dirke
        GROUP BY d.id, d.datum, d.ime_dirkalisca
        ORDER BY d.id
    """)
    dirke = cur.fetchall()

    if not dirka:
        print("\n⚠️ Trenutno ni prijavljenih uporabnikov.")
        return None

    print("\n🏁 Trenutne dirke:")
    for dirka in dirke:
        print(f"📅 ID: {dirka[0]}, Datum: {dirka[1]}, Lokacija: {dirka[2]}, Prijavljeni: {dirka[3]}/20")

    return dirke


def doloci_rezultate(cur, conn):
    # Prikaži vse dirke, da admin izbere eno
    dirke = prikazi_trenutno_dirko(cur)

    if not dirke:
        print("⚠️ Ni aktivnih dirk za določanje rezultatov.")
        return

    # Izberi ID dirke
    while True:
        try:
            id_dirke = int(input("\n🔢 Vnesi ID dirke, ki jo želiš urediti: "))
            cur.execute("SELECT * FROM Dirka WHERE id = %s", (id_dirke,))
            if cur.fetchone():
                break
            else:
                print("⚠️ Neveljaven ID. Poskusi znova.")
        except ValueError:
            print("⚠️ Vnesi veljavno številko.")

    # Pridobi vse prijavljene za to dirko
    cur.execute("""
        SELECT uporabnisko_ime 
        FROM TrenutnaDirka 
        WHERE id_dirke = %s 
        ORDER BY uporabnisko_ime
    """, (id_dirke,))
    prijavljeni = [uporabnik[0] for uporabnik in cur.fetchall()]

    if not prijavljeni:
        print("⚠️ Ni prijavljenih uporabnikov za to dirko.")
        return

    # Vpiši rezultate
    rezultati = []
    tocke_f1 = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1] + [0] * (len(prijavljeni) - 10)

    print("\n🏆 Vpiši rezultate (od 1. mesta naprej):")
    for mesto, uporabnik in enumerate(prijavljeni, start=1):
        print(f"{mesto}. {uporabnik}")
        rezultati.append((id_dirke, uporabnik, mesto, tocke_f1[mesto - 1]))

    # Shrani rezultate v bazo
    for rezultat in rezultati:
        cur.execute("""
            INSERT INTO RezultatDirke (id_dirke, uporabnisko_ime, uvrstitev, tocke) 
            VALUES (%s, %s, %s, %s)
        """, rezultat)
        
        # Posodobi točke uporabnika
        cur.execute("""
            UPDATE Uporabnik 
            SET tocke = tocke + %s 
            WHERE uporabnisko_ime = %s
        """, (rezultat[3], rezultat[1]))

    conn.commit()
    print("\n✅ Rezultati uspešno shranjeni!")


def prikazi_profil_admin(cur, conn, admin):
    cur.execute("SELECT ime, priimek FROM Boss WHERE uporabnisko_ime = %s", (admin,))
    rezultat = cur.fetchone()
    if rezultat:
        ime, priimek = rezultat

        print(f"\n👤 Profil: {ime} {priimek}")
        
        print("\n📌 Uredi profil:")
        print("1️⃣ Spremeni geslo")
        print("2️⃣ Nazaj")

        izbira = input("\n🔢 Izberi možnost: ").strip()

        if izbira == "1":
            novo_geslo = input("🔒 Vnesi novo geslo: ").strip()
            cur.execute("UPDATE Boss SET geslo = %s WHERE uporabnisko_ime = %s", (novo_geslo, admin))
            conn.commit()
            print("\n✅ Geslo uspešno spremenjeno!")


def admin_menu(cur, conn):
    admin = prijava_admin(cur)
    if not admin:
        return

    while True:
        print("\n--- ADMIN MENU ---")
        print("1️⃣ Profil")
        print("2️⃣ Dodaj novega admina")
        print("3️⃣ Preglej trenutno dirko")
        print("4️⃣ Določi rezultate dirke")
        print("5️⃣ Izhod")

        izbira = input("Izberi možnost: ").strip()

        if izbira == "1":
            prikazi_profil_admin(cur,conn,admin)
        elif izbira == "2":
            dodaj_admina(cur, conn)
        elif izbira == "3":
            prikazi_trenutno_dirko(cur)
        elif izbira == "4":
            doloci_rezultate(cur, conn)
        elif izbira == "5":
            print("\n👋 Izhod iz admin panela.")
            break
        else:
            print("\n⚠️ Napačna izbira, poskusi znova.")
