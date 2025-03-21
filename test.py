from dostop import ustvari_povezavo

conn = ustvari_povezavo()
cur = conn.cursor()
cur.execute("SELECT * FROM Uporabnik LIMIT 5")
rezultati = cur.fetchall()

for vrstica in rezultati:
    print(vrstica)

conn.close()