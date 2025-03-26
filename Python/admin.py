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
    # Poizvedba za vse dirke s številom prijavljenih
    cur.execute("""
        SELECT d.id, d.datum, d.ime_dirkalisca, COUNT(td.uporabnisko_ime) 
        FROM Dirka d
        LEFT JOIN TrenutnaDirka td ON d.id = td.id_dirke
        GROUP BY d.id, d.datum, d.ime_dirkalisca
        ORDER BY d.id
    """)
    vse_dirke = cur.fetchall()

    # Pridobi ID-jev dirk, ki so že končane (vsaj 10 vnosov v RezultatDirke s točkami)
    cur.execute("""
        SELECT id_dirke
        FROM RezultatDirke
        WHERE tocke > 0
        GROUP BY id_dirke
        HAVING COUNT(*) >= 10
    """)
    koncane_dirke_ids = {dirka[0] for dirka in cur.fetchall()}  # Uporabimo množico za hitrejše iskanje

    dirke = []
    koncane_dirke = []

    for dirka in vse_dirke:
        if dirka[0] in koncane_dirke_ids:
            koncane_dirke.append(dirka)
        else:
            dirke.append(dirka)

    # Prikaz aktivnih dirk
    if dirke:
        print("\n🏁 Trenutne dirke:")
        for dirka in dirke:
            print(f"📅 ID: {dirka[0]}, Datum: {dirka[1]}, Dirka: {dirka[2]}, Prijavljeni: {dirka[3]}/20")
    else:
        print("\n🚫 Ni aktivnih dirk.")

    # Prikaz končanih dirk
    if koncane_dirke:
        print("\n🏆 Končane dirke:")
        for dirka in koncane_dirke:
            print(f"✅ ID: {dirka[0]}, Datum: {dirka[1]}, Dirka: {dirka[2]}, Prijavljeni: {dirka[3]}/20")
    else:
        print("\n🚫 Ni končanih dirk.")

    return dirke


def doloci_rezultate(cur, conn):
    dirke = prikazi_trenutno_dirko(cur)

    while True:
        id_dirke = input("\n🔢 Vnesi ID dirke za določanje rezultatov (ali 0 za nazaj): ").strip()
        if id_dirke == "0":
            print("🔙 Vračam te nazaj v meni.")
            return

        cur.execute("SELECT * FROM Dirka WHERE id = %s", (id_dirke,))
        if not cur.fetchone():
            print("\n⚠️ Neveljaven ID dirke. Poskusi znova.")
            continue

        cur.execute("""
            SELECT COUNT(*) FROM RezultatDirke 
            WHERE id_dirke = %s AND tocke > 0
        """, (id_dirke,))
        if cur.fetchone()[0] >= 10:
            print("\n❌ Ta dirka je že zaključena! Ne moreš več vnesti rezultatov.")
            continue

        cur.execute("SELECT uporabnisko_ime FROM TrenutnaDirka WHERE id_dirke = %s ORDER BY uporabnisko_ime", (id_dirke,))
        prijavljeni = [uporabnik[0] for uporabnik in cur.fetchall()]

        if not prijavljeni:
            print("\n⚠️ Ni prijavljenih uporabnikov za to dirko.")
            return

        if len(prijavljeni) < 10:
            print("\n⚠️ Premalo tekmovalcev za točkovanje!")
            return

        tocke_f1 = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1] + [0] * (len(prijavljeni) - 10)
        rezultati = []

        print('Tekmovali so:')
        for uporabnik in enumerate(prijavljeni, start=1):
            print(f"{uporabnik}")

        print("\n🏆 Vpiši rezultate (od 1. mesta naprej):")
        i = 0
        while i < min(20, len(prijavljeni)):
            uporabnik = input(f"{i+1}. mesto: ").strip()
            if uporabnik not in prijavljeni:
                print("\n⚠️ Napačno uporabniško ime. Poskusi znova.")
                continue

            rezultati.append(uporabnik)
            i += 1

        for i, uporabnik in enumerate(rezultati):
            cur.execute("""
                INSERT INTO RezultatDirke (id_dirke, uporabnisko_ime, uvrstitev, tocke)
                VALUES (%s, %s, %s, %s)
            """, (id_dirke, uporabnik, i+1, tocke_f1[i]))

            cur.execute("""
                UPDATE Uporabnik SET tocke = tocke + %s WHERE uporabnisko_ime = %s
            """, (tocke_f1[i], uporabnik))

        conn.commit()
        print("\n✅ Rezultati uspešno shranjeni!")
        return




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

def prikazi_rezultate_dirke(cur):
    # Pridobi vse dirke, ki so že vpisane v RezultatDirke
    cur.execute("""
        SELECT DISTINCT d.id, d.datum, d.ime_dirkalisca
        FROM Dirka d
        JOIN RezultatDirke r ON d.id = r.id_dirke
        ORDER BY d.datum DESC
    """)
    dirke = cur.fetchall()

    if not dirke:
        print("\n🚫 Ni preteklih dirk z rezultati.")
        return

    # Prikaz izbire dirke
    print("\n🏆 Pretekle dirke z rezultati:")
    for dirka in dirke:
        print(f"📅 ID: {dirka[0]}, Datum: {dirka[1]}, Dirka: {dirka[2]}")

    while True:
        try:
            id_dirke = int(input("\n🔢 Vnesi ID dirke, katere rezultate želiš videti: "))
            cur.execute("""
                SELECT r.uvrstitev, r.uporabnisko_ime, r.tocke
                FROM RezultatDirke r
                WHERE r.id_dirke = %s
                ORDER BY r.uvrstitev ASC
            """, (id_dirke,))
            rezultati = cur.fetchall()

            if rezultati:
                print("\n🏁 Rezultati dirke:")
                for vrstica in rezultati:
                    print(f"🥇 {vrstica[0]}. {vrstica[1]} - {vrstica[2]} točk")
                break
            else:
                print("⚠️ Ni rezultatov za to dirko. Poskusi znova.")
        except ValueError:
            print("⚠️ Vnesi veljaven ID dirke.")

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
        print("5️⃣ Poglej rezultate preteklih dirk")
        print("6️⃣ Izhod")

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
            prikazi_rezultate_dirke(cur)
        elif izbira == "6":
            print("\n👋 Izhod iz admin panela.")
            break
        else:
            print("\n⚠️ Napačna izbira, poskusi znova.")
