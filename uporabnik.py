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
    except Exception as e:
        print("❌ Napaka:", e)
        conn.rollback()
    finally:
        cur.close()
        conn.close()

glavna()