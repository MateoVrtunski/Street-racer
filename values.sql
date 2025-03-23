INSERT INTO Avto (id, znamka, model, moc, max_hitrost) VALUES
(1, 'Aston Martin', 'DBS Superleggera', 725 , 211),
(2, 'Ferrari', 'SF90 Stradale', 1000 , 340),
(3, 'BMW', 'M5 Competition', 625 , 305),
(4, 'Mercedes-Benz', 'AMG GT Black Series', 730 , 325),
(5, 'Porsche', '911 Turbo S', 650 , 330),
(6, 'Lamborghini', 'Aventador SVJ', 770 , 352),
(7, 'Bugatti', 'Chiron Super Sport 300+', 1600 , 490),
(8, 'McLaren', 'Speedtail', 1050 , 403),
(9, 'Pagani', 'Huayra Roadster BC', 800 , 370),
(10, 'Koenigsegg', 'Jesko Absolut', 1600 , 531),
(11, 'Aston Martin', 'Vantage AMR', 510 , 314),
(12, 'Ferrari', 'LaFerrari', 950 , 352),
(13, 'BMW', 'i8', 374 , 250),
(14, 'Mercedes-Benz', 'SLS AMG', 571 , 317),
(15, 'Porsche', '918 Spyder', 887 , 340),
(16, 'Lamborghini', 'Huracán Evo', 640 , 325),
(17, 'Bugatti', 'Veyron 16.4', 1001 , 407),
(18, 'McLaren', '720S', 720 , 341),
(19, 'Pagani', 'Zonda Cinque', 678 , 350),
(20, 'Koenigsegg', 'Agera RS', 1160 , 447);

INSERT INTO dirkalisce (id, ime_dirkalisca, mesto, drzava) VALUES
(1, 'Grand Prix Pariza', 'Pariz', 'Francija'),
(2, 'Tokyo Night Sprint', 'Tokyo', 'Japonska'),
(3, 'Barcelona Street Challenge', 'Barcelona', 'Španija'),
(4, 'Ljubljana City Circuit', 'Ljubljana', 'Slovenija'),
(5, 'New York Skyline Race', 'New York', 'ZDA'),
(6, 'London River Run', 'London', 'Velika Britanija'),
(7, 'Sydney Harbour Dash', 'Sydney', 'Avstralija'),
(8, 'Berlin Wall GP', 'Berlin', 'Nemčija'),
(9, 'Rome Colosseum Circuit', 'Rim', 'Italija'),
(10, 'Moscow Midnight Run', 'Moskva', 'Rusija'),
(11, 'Dubai Desert Drift', 'Dubaj', 'Združeni arabski emirati'),
(12, 'Cape Town Coastal Cruise', 'Cape Town', 'Južnoafriška republika'),
(13, 'Toronto Downtown Dash', 'Toronto', 'Kanada'),
(14, 'Rio Carnival Circuit', 'Rio de Janeiro', 'Brazilija'),
(15, 'Shanghai Skyline Sprint', 'Šanghaj', 'Kitajska'),
(16, 'Seoul Speed Challenge', 'Seul', 'Južna Koreja'),
(17, 'Istanbul Bridge Battle', 'Istanbul', 'Turčija'),
(18, 'Athens Acropolis Rally', 'Atene', 'Grčija'),
(19, 'Helsinki Midnight Circuit', 'Helsinki', 'Finska'),
(20, 'Vienna Ringstrasse GP', 'Dunaj', 'Avstrija');

INSERT INTO dirka (id, datum, vreme, id_dirkalisca) VALUES
(1, '2025-03-15', 'jasno', 1),
(2, '2025-04-10', 'oblačno', 2),
(3, '2025-05-05', 'jasno', 3),
(4, '2025-06-20', 'jasno', 4),
(5, '2025-07-12', 'jasno', 5),
(6, '2025-08-25', 'šibek dež', 6),
(7, '2025-09-14', 'jasno', 7),
(8, '2025-10-03', 'oblačno', 8),
(9, '2025-11-09', 'močen dež', 9),
(10, '2025-12-01', 'sneg', 10),
(11, '2025-03-28', 'jasno', 11),
(12, '2025-04-18', 'jasno', 12),
(13, '2025-05-22', 'oblačno', 13),
(14, '2025-06-05', 'jasno', 14),
(15, '2025-07-30', 'jasno', 15),
(16, '2025-08-16', 'šibek dež', 16),
(17, '2025-09-21', 'jasno', 17),
(18, '2025-10-12', 'močen dež', 18),
(19, '2025-11-07', 'oblačno', 19),
(20, '2025-12-15', 'sneg', 20),
(21, '2026-01-10', 'sneg', 19),
(22, '2026-02-14', 'oblačno', 18),
(23, '2026-03-08', 'jasno', 17),
(24, '2026-04-03', 'jasno', 16),
(25, '2026-05-19', 'jasno', 15),
(26, '2026-06-25', 'jasno', 14),
(27, '2026-07-14', 'jasno', 13),
(28, '2026-08-09', 'šibek dež', 12),
(29, '2026-09-27', 'oblačno', 11),
(30, '2026-10-20', 'močen dež', 10);

select * from uporabnik

ALTER TABLE Dirka
ADD COLUMN ime_dirkalisca VARCHAR(100);
UPDATE Dirka d
SET ime_dirkalisca = dl.ime_dirkalisca
FROM Dirkalisce dl
WHERE d.id_dirkalisca = dl.id;

INSERT INTO uporabnik (id, uporabnisko_ime, ime, priimek, tocke, id_avto) VALUES
(1, 'goat', 'Fernando', 'Alonso', 10, 1);

