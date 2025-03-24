from dostop import ustvari_povezavo

db = 'sem2024_mateov'
host = 'baza.fmf.uni-lj.si'
user = 'javnost'
password = 'javnogeslo'

def prijava_uporabnika(cur):
    print("\n🔐 Prijava:")

    uporabnisko_ime = input("Vnesi svoje uporabniško ime: ").strip()
    geslo = input("Vnesi svoje geslo: ").strip()

    cur.execute("""
        SELECT * FROM Uporabnik
        WHERE uporabnisko_ime = %s AND geslo = %s
    """, (uporabnisko_ime, geslo))

    rezultat = cur.fetchone()

    if rezultat:
        print(f"\n✅ Prijavljen si kot: {rezultat[2]} {rezultat[3]} (Uporabniško ime: {rezultat[1]})\n")
        return uporabnisko_ime
    else:
        print("\n⚠️ Napačno uporabniško ime ali geslo. Poskusi znova!\n")
        return None
    
def prikazi_dirke(cur):
    cur.execute("""
        SELECT d.id, d.datum, d.vreme, dl.ime_dirkalisca
        FROM Dirka d
        JOIN Dirkalisce dl ON d.id_dirkalisca = dl.id
        ORDER BY d.datum
    """)
    dirke = cur.fetchall()

    print("\n🏁 Razpoložljive dirke:")
    for dirka in dirke:
        print(f"➡️ ID: {dirka[0]}, Datum: {dirka[1]}, Vreme: {dirka[2]}, Dirkališče: {dirka[3]}")
    
    return dirke

def registracija_uporabnika(cur):
    print("\n📝 Registracija novega uporabnika:")

    ime = input("Vnesi svoje ime: ").strip()
    priimek = input("Vnesi svoj priimek: ").strip()

    # Preverimo edinstvenost uporabniškega imena
    while True:
        uporabnisko_ime = input("Izberi uporabniško ime: ").strip()
        cur.execute("SELECT 1 FROM Uporabnik WHERE uporabnisko_ime = %s", (uporabnisko_ime,))
        if cur.fetchone():
            print("⚠️ Uporabniško ime je že zasedeno, prosim izberi drugo.")
        else:
            break

    geslo = input("Izberi geslo: ").strip()

    # Prikažemo vse avte
    cur.execute("SELECT id, znamka, model, moc, max_hitrost FROM Avto ORDER BY id")
    avti = cur.fetchall()
    if not avti:
        print("⚠️ Ni razpoložljivih avtov! Najprej jih dodaj v bazo.")
        return

    print("\nRazpoložljivi avti:")
    for avto in avti:
        print(f"{avto[0]}: {avto[1]} {avto[2]} (Moč: {avto[3]} KM, Max hitrost: {avto[4]} km/h)")

    while True:
        try:
            id_avto = int(input("Izberi ID avta: "))
            cur.execute("SELECT znamka, model FROM Avto WHERE id = %s", (id_avto,))
            avto_podatki = cur.fetchone()

            if avto_podatki:
                ime_avta = f"{avto_podatki[0]} {avto_podatki[1]}"
                break
            else:
                print("⚠️ Napačen ID avta. Poskusi znova.")
        except ValueError:
            print("⚠️ Vpiši številko za ID avta.")

    # Določimo naslednji ID uporabnika
    cur.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM Uporabnik")
    nov_id = cur.fetchone()[0]

    # Vnos v bazo
    cur.execute("""
        INSERT INTO Uporabnik (id, uporabnisko_ime, geslo, ime, priimek, tocke, id_avto, model_avta)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (nov_id, uporabnisko_ime, geslo, ime, priimek, 0, id_avto, ime_avta))

    print(f"✅ Uporabnik '{uporabnisko_ime}' uspešno registriran!\n")


def izberi_dirko(cur, uporabnik):
    dirke = prikazi_dirke(cur)
    
    izbrani_id = input("\nVnesi ID dirke, na katero se želiš prijaviti: ").strip()

    cur.execute("SELECT * FROM Dirka WHERE id = %s", (izbrani_id,))
    dirka = cur.fetchone()

    if dirka:
        print(f"\n✅ Uspešno si izbral dirko z ID: {dirka[0]}, Datum: {dirka[1]}")

        # Simulacija "prijave" -> vstavimo v RezultatDirke z začetnimi podatki
        cur.execute("""
            INSERT INTO RezultatDirke (id_dirke, uporabnisko_ime, uvrstitev, tocke)
            VALUES (%s, %s, NULL, 0)
            ON CONFLICT (id_dirke, uporabnisko_ime) DO NOTHING
        """, (izbrani_id, uporabnik))
        print("✅ Prijavljen si na dirko!")
        return True
    else:
        print("\n⚠️ Neveljaven ID dirke. Poskusi znova.")
        return False
    
def glavna():
    conn, cur = ustvari_povezavo()

    try:
        uporabnik = None  # Najprej ni noben prijavljen

        # Ta while loop bo tekla, dokler ne bo veljavna izbira
        while uporabnik is None:
            print("\n👋 Dobrodošel!")
            print("1️⃣ Prijava")
            print("2️⃣ Registracija")
            izbira = input("Izberi (1 ali 2): ").strip()

            if izbira == '1':
                uporabnik = prijava_uporabnika(cur)
                if uporabnik:
                    prijava_uspesna = izberi_dirko(cur, uporabnik)

                    if prijava_uspesna:
                        conn.commit()
                        print("\n✅ Vse spremembe so shranjene!")
                    else:
                        print("\n⚠️ Ni prijave na dirko.")
                else:
                    print("\n⚠️ Prijava neuspešna.")
                    # uporabnik ostane None, zato se loop nadaljuje

            elif izbira == '2':
                uporabnik = registracija_uporabnika(cur)
                conn.commit()  # Shranimo registracijo
                print("\n✅ Registracija uspešna!")

                prijava_uspesna = izberi_dirko(cur, uporabnik)

                if prijava_uspesna:
                    conn.commit()
                    print("\n✅ Vse spremembe so shranjene!")
                else:
                    print("\n⚠️ Ni prijave na dirko.")
            else:
                print("\n⚠️ Napačna izbira! Prosim vnesi 1 za prijavo ali 2 za registracijo.\n")

    except Exception as e:
        print("❌ Napaka:", e)
        conn.rollback()
    finally:
        cur.close()
        conn.close()

glavna()