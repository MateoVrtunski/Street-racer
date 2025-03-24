from dostop import ustvari_povezavo

db = 'sem2024_mateov'
host = 'baza.fmf.uni-lj.si'
user = 'javnost'
password = 'javnogeslo'

def prijava_uporabnika(cur):
    uporabnik = input("Vnesi svoje uporabniško ime: ").strip()
    
    cur.execute("SELECT * FROM Uporabnik WHERE uporabnisko_ime = %s", (uporabnik,))
    rezultat = cur.fetchone()

    if rezultat:
        print(f"\n✅ Prijavljen si kot: {rezultat[2]} {rezultat[3]} (Uporabniško ime: {rezultat[1]})\n")
        return uporabnik
    else:
        print("\n⚠️ Uporabniško ime ne obstaja. Prosim registriraj se najprej!\n")
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
    print("\n🔧 Registracija novega uporabnika:")
    
    ime = input("Vnesi svoje ime: ").strip()
    priimek = input("Vnesi svoj priimek: ").strip()
    
    while True:
        uporabnisko_ime = input("Izberi uporabniško ime: ").strip()
        
        # Preveri, če uporabniško ime že obstaja
        cur.execute("SELECT * FROM Uporabnik WHERE uporabnisko_ime = %s", (uporabnisko_ime,))
        if cur.fetchone():
            print("⚠️ To uporabniško ime že obstaja. Izberi drugo.")
        else:
            break

    # Prikaži seznam avtov
    cur.execute("SELECT id, znamka, model FROM Avto ORDER BY id")
    avti = cur.fetchall()

    print("\n🚗 Seznam razpoložljivih avtov:")
    for avto in avti:
        print(f"ID: {avto[0]} ➡️ {avto[1]} {avto[2]}")

    while True:
        try:
            izbran_avto_id = int(input("\nVnesi ID avta, ki ga želiš izbrati: ").strip())
            
            # Preveri, če avto obstaja
            cur.execute("SELECT * FROM Avto WHERE id = %s", (izbran_avto_id,))
            avto = cur.fetchone()
            
            if avto:
                print(f"\n✅ Izbral si {avto[1]} {avto[2]}.")
                break
            else:
                print("⚠️ Avto z izbranim ID-jem ne obstaja. Poskusi znova.")
        except ValueError:
            print("⚠️ Prosim, vnesi številko ID-ja.")

    # Poišči največji obstoječi ID uporabnika in povečaj za 1
    cur.execute("SELECT MAX(id) FROM Uporabnik")
    zadnji_id = cur.fetchone()[0]
    nov_id = (zadnji_id or 0) + 1

    # Vstavi novega uporabnika v bazo
    cur.execute("""
        INSERT INTO Uporabnik (id, uporabnisko_ime, ime, priimek, tocke, id_avto)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nov_id, uporabnisko_ime, ime, priimek, 0, izbran_avto_id))

    print(f"\n🎉 Uporabnik {ime} {priimek} uspešno registriran z uporabniškim imenom '{uporabnisko_ime}' in ID-jem {nov_id}!\n")

    return uporabnisko_ime  # Lahko vrneš, da ga avtomatsko prijaviš naprej

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