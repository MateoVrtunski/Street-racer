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
            "INSERT INTO Boss (id, uporabnisko_ime, geslo, ime, priimek, tocke, id_avto, model_avta) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (nov_id, uporabnik[1], uporabnik[2], uporabnik[3], uporabnik[4], uporabnik[5], uporabnik[6], uporabnik[7])
        )
        conn.commit()
        print(f"✅ Uporabnik {uporabnisko_ime} je zdaj admin!")


def prikazi_trenutno_dirko(cur):
    print("\n🏁 Prijavljeni na trenutno dirko:")
    cur.execute("""
        SELECT id_dirke, uporabnisko_ime, model_avta FROM TrenutnaDirka ORDER BY id_dirke
    """)
    dirka = cur.fetchall()

    if not dirka:
        print("\n⚠️ Trenutno ni prijavljenih uporabnikov.")
        return None

    for idx, (id_dirke, uporabnisko_ime, model_avta) in enumerate(dirka, start=1):
        print(f"{idx}. {uporabnisko_ime} - {model_avta} (Dirka ID: {id_dirke})")

    return dirka

def doloci_rezultate(cur, conn):
    dirka = prikazi_trenutno_dirko(cur)
    if not dirka:
        return

    # F1 točkovanje
    tocke_f1 = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]

    rezultati = []
    for i in range(len(dirka)):
        uporabnik = input(f"Vnesi uporabnika, ki je {i+1}. mesto: ").strip()
        rezultati.append(uporabnik)

    for i, uporabnik in enumerate(rezultati):
        tocke = tocke_f1[i] if i < 10 else 0

        # Vstavi rezultat v tabelo
        cur.execute("""
            INSERT INTO RezultatDirke (id_dirke, uporabnisko_ime, uvrstitev, tocke)
            VALUES (%s, %s, %s, %s)
        """, (dirka[0][0], uporabnik, i+1, tocke))

        # Posodobi točke pri uporabniku
        cur.execute("""
            UPDATE Uporabnik
            SET tocke = tocke + %s
            WHERE uporabnisko_ime = %s
        """, (tocke, uporabnik))

    conn.commit()
    print("\n✅ Rezultati so bili uspešno shranjeni!")


def prikazi_profil_admin(cur, conn, admin):
    cur.execute("SELECT ime, priimek, tocke, id_avto FROM Boss WHERE uporabnisko_ime = %s", (admin,))
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
            cur.execute("UPDATE Boss SET geslo = %s WHERE uporabnisko_ime = %s", (novo_geslo, admin))
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
                    cur.execute("UPDATE Boss SET id_avto = %s WHERE uporabnisko_ime = %s", (nov_avto_id, admin))
                    conn.commit()
                    print("\n✅ Avto uspešno posodobljen!")
                    break
                else:
                    print("⚠️ Neveljaven ID avta. Poskusi znova.")

def admin_menu(cur, conn):
    admin = prijava_admin(cur)
    if not admin:
        return

    while True:
        print("\n--- ADMIN MENU ---")
        print("1️⃣ Spremeni profil")
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
