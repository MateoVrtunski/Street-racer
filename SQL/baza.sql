CREATE TABLE Avto (
    id INTEGER PRIMARY KEY,
    znamka VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    moc INTEGER,
    max_hitrost INTEGER
);

CREATE TABLE Dirkalisce (
    id INTEGER PRIMARY KEY,
    ime_dirkalisca VARCHAR(100),
    mesto VARCHAR(50),
    drzava VARCHAR(50)
);

CREATE TABLE Uporabnik (
    id INTEGER PRIMARY KEY,
    uporabnisko_ime VARCHAR(50) UNIQUE NOT NULL,
    geslo VARCHAR(255) NOT NULL,
    ime VARCHAR(50) NOT NULL,
    priimek VARCHAR(50) NOT NULL,
    tocke INTEGER DEFAULT 0,
    id_avto INTEGER, 
    model_avta VARCHAR(100),
    FOREIGN KEY (id_avto) REFERENCES Avto(id) ON DELETE SET NULL
);

CREATE TABLE Dirka (
    id INTEGER PRIMARY KEY,
    datum DATE NOT NULL,
    vreme VARCHAR(50),
    id_dirkalisca INTEGER, 
    ime_dirkalisca VARCHAR(100),
    FOREIGN KEY (id_dirkalisca) REFERENCES Dirkalisce(id) ON DELETE SET NULL
);

CREATE TABLE RezultatDirke (
    id_dirke INTEGER,
    uporabnisko_ime VARCHAR(50) NOT NULL,
    uvrstitev INTEGER NOT NULL,
    tocke INTEGER NOT NULL,
    PRIMARY KEY (id_dirke, uporabnisko_ime), 
    FOREIGN KEY (id_dirke) REFERENCES Dirka(id) ON DELETE SET NULL, 
    FOREIGN KEY (uporabnisko_ime) REFERENCES Uporabnik(uporabnisko_ime) ON DELETE SET NULL 
);

UPDATE Dirka d
SET ime_dirkalisca = dl.ime_dirkalisca
FROM Dirkalisce dl
WHERE d.id_dirkalisca = dl.id;