from dostop import ustvari_povezavo

def prijava(uporabnisko_ime):
    conn = ustvari_povezavo()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Uporabnik WHERE uporabnisko_ime = ?", (uporabnisko_ime,))
    uporabnik = cur.fetchone()
    conn.close()
    return uporabnik

def seznam_dirkalisca():
    conn = ustvari_povezavo()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Dirkalisce")
    dirkalisca = cur.fetchall()
    conn.close()
    return dirkalisca

def dodaj_rezultat(id_dirke, uporabnisko_ime, uvrstitev, tocke):
    conn = ustvari_povezavo()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO RezultatDirke (id_dirke, uporabnisko_ime, uvrstitev, tocke)
        VALUES (?, ?, ?, ?)
    """, (id_dirke, uporabnisko_ime, uvrstitev, tocke))
    
    # Posodobi skupne točke uporabnika
    cur.execute("""
        UPDATE Uporabnik SET tocke = tocke + ?
        WHERE uporabnisko_ime = ?
    """, (tocke, uporabnisko_ime))

    conn.commit()
    conn.close()

def seznam_dirk():
    conn = ustvari_povezavo()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Dirka")
    dirke = cur.fetchall()
    conn.close()
    return dirke