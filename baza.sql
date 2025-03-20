CREATE TABLE Avto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    znamka VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    moc INTEGER,
    max_hitrost INTEGER
);

CREATE TABLE Dirkalisce (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ime_dirkalisca VARCHAR(100),
    mesto VARCHAR(50),
    drzava VARCHAR(50)
);

CREATE TABLE Uporabnik (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uporabnisko_ime VARCHAR(50) UNIQUE NOT NULL,
    ime VARCHAR(50) NOT NULL,
    priimek VARCHAR(50) NOT NULL,
    tocke INTEGER DEFAULT 0,
    id_avto INTEGER, -- tuji ključ za avto
    FOREIGN KEY (id_avto) REFERENCES Avto(id) ON DELETE SET NULL
);

CREATE TABLE Dirka (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datum DATE NOT NULL,
    vreme VARCHAR(50),
    id_dirkalisca INTEGER, --tuji ključ za dirkališče
    FOREIGN KEY (id_dirkalisca) REFERENCES Dirkalisce(id) ON DELETE SET NULL
);

CREATE TABLE RezultatDirke (
    id_dirke INTEGER,
    uporabnisko_ime VARCHAR(50) NOT NULL,
    uvrstitev INTEGER NOT NULL,
    tocke INTEGER NOT NULL,
    PRIMARY KEY (id_dirke, uporabnisko_ime), -- kombinirani primarni ključ
    FOREIGN KEY (id_dirke) REFERENCES Dirka(id) ON DELETE SET NULL, --tuji ključ za dirko
    FOREIGN KEY (uporabnisko_ime) REFERENCES Uporabnik(uporabnisko_ime) ON DELETE SET NULL --tuji ključ za uporabnika
);