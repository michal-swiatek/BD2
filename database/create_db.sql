CREATE TABLE IF NOT EXISTS administrator (
    id INT NOT NULL,
    CONSTRAINT admin_pk PRIMARY KEY( id )
);

CREATE TABLE IF NOT EXISTS budynek (
    id            	INT NOT NULL,
    nazwa            	VARCHAR(40),
    ulica             	VARCHAR(40) NOT NULL,
    numer            	INT NOT NULL,
    kod_pocztowy      	VARCHAR(7) NOT NULL,
    miasto_id  	INT NOT NULL,
    CONSTRAINT budynek_pk PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS dane_kontaktowe (
    id                 	INT NOT NULL,
    kontakt                    VARCHAR(50) NOT NULL,
    typ_kontaktu_typ           VARCHAR(20) NOT NULL,
    firma_cateringowa_id  	INT,
    uzytkownik_id   		INT,
    CONSTRAINT dane_kontaktowe_pk PRIMARY KEY (id),
    CONSTRAINT arc_dane CHECK( 
   		 ( ( firma_cateringowa_id IS NOT NULL ) AND ( uzytkownik_id IS NULL ) )
             OR ( ( uzytkownik_id IS NOT NULL ) AND ( firma_cateringowa_id IS NULL ) ) ),
    CONSTRAINT dane_unique UNIQUE ( kontakt, typ_kontaktu_typ )
);

CREATE TABLE IF NOT EXISTS dodatkowa_obsluga (
    id  	 INT NOT NULL,
    obsluga     VARCHAR(50) NOT NULL,
    opis        TEXT,
    cena        INT NOT NULL, 
    CONSTRAINT  dodatkowa_obsluga_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS dodatkowy_atrybut (
    id   	INT NOT NULL,
    atrybut  	VARCHAR(30) NOT NULL,
    opis     	TEXT, 
    CONSTRAINT dodatkowy_atrybut_pk PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS dostepnosc_atrybutu (
    sala_id            	INT NOT NULL,
    dodatkowy_atrybut_id  	INT NOT NULL,
    CONSTRAINT dostepnosc_atrybutu_pk PRIMARY KEY ( sala_id, dodatkowy_atrybut_id )
);

CREATE TABLE IF NOT EXISTS dostepnosc_sprzetu (
    liczba            INT NOT NULL,
    sala_id      INT NOT NULL,
    sprzet_id  INT NOT NULL,
    CONSTRAINT dostepnosc_sprzetu_pk PRIMARY KEY( sala_id, sprzet_id)
);

CREATE TABLE IF NOT EXISTS firma_cateringowa (
    id        	    	INT NOT NULL,
    nazwa           	VARCHAR(60) NOT NULL,
    limit_zamowien  	INT NOT NULL, 
    CONSTRAINT firma_cateringowa_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS kierownik (
    id 		INT NOT NULL, 
    CONSTRAINT kierownik_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS klasyfikacja_produktu (
    klasa     		VARCHAR(50) NOT NULL,
    id  		INT NOT NULL,
    CONSTRAINT klasyfikacja_produktu_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS komorka_organizacyjna (
    nazwa         	VARCHAR(30) NOT NULL,
    id    		INT NOT NULL,
    kierownik_id  	INT NOT NULL,
    CONSTRAINT komorka_organizacyjna_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS miasto (
    id  		INT NOT NULL,
    nazwa      	VARCHAR(40) NOT NULL,
    CONSTRAINT miasto_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS pozycja (
    liczba               	INT,
    produkt_spozywczy_id  	INT NOT NULL,
    zamowienie_id       	INT NOT NULL,
    CONSTRAINT pozycja_pk PRIMARY KEY (produkt_spozywczy_id, zamowienie_id)
);


CREATE TABLE IF NOT EXISTS pracownik (
    id                        INT NOT NULL,
    komorka_organizacyjna_id  INT NOT NULL, 
    CONSTRAINT pracownik_pk PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS produkt_spozywczy (
    id               		 INT NOT NULL,
    cena                        INT NOT NULL,
    max_zamowienie              INT,
    firma_cateringowa_id  	 INT NOT NULL,
    opis                        TEXT,
    CONSTRAINT produkt_spozywczy_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS projekt (
    nazwa                     VARCHAR(120) NOT NULL,
    id               	       INT NOT NULL,
    komorka_organizacyjna_id  INT, 
    CONSTRAINT projekt_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS przypisanie_produktu (
    produkt_spozywczy_id   INT NOT NULL,
    klasyfikacja_produktu_id INT NOT NULL, 
    CONSTRAINT przypisanie_produktu_pk PRIMARY KEY ( produkt_spozywczy_id, klasyfikacja_produktu_id)
);
CREATE TABLE IF NOT EXISTS rezerwacja (
    id              		INT NOT NULL,
    rozpoczecie          	DATETIME NOT NULL,
    zakonczenie          	DATETIME NOT NULL,
    sala_id         		INT NOT NULL,
    cel                  	VARCHAR(120),
    projekt_id  		INT NOT NULL,
    zamowienie_id        	INT,
    koszt                	INT NOT NULL,
    CONSTRAINT rezerwacja_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS rezerwacja_obslugi (
    dodatkowa_obsluga_id INT NOT NULL,
    rezerwacja_id      INT NOT NULL,
    CONSTRAINT rezerwacja_obslugi_pk PRIMARY KEY (dodatkowa_obsluga_id, rezerwacja_id) 
);


CREATE TABLE IF NOT EXISTS rodzaj_sprzetu (
    rodzaj   VARCHAR(40) NOT NULL,
    id  INT NOT NULL, 
    CONSTRAINT rodzaj_sprzetu_pk PRIMARY KEY (id)
);


CREATE TABLE IF NOT EXISTS sala (
    id          	INT NOT NULL,
    powierzchnia      	INT NOT NULL,
    numer_sali        	INT NOT NULL,
    budynek_id    	INT NOT NULL,
    miejsca_siedzace  	INT NOT NULL,
    miejsca_stojace   	INT NOT NULL, 
    CONSTRAINT sala_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS sprzet (
    model                   VARCHAR(50) NOT NULL,
    id                      INT NOT NULL,
    rodzaj_sprzetu_id INT NOT NULL,
    CONSTRAINT sprzet_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS typ_kontaktu (
    typ VARCHAR(20) NOT NULL, 
    CONSTRAINT typ_kontaktu_pk PRIMARY KEY (typ)
);


CREATE TABLE IF NOT EXISTS uzytkownik (
    id          INT NOT NULL,
    imie        VARCHAR(60) NOT NULL,
    nazwisko    VARCHAR(100) NOT NULL,
    login       VARCHAR(40) NOT NULL,
    hash_hasla  INT NOT NULL,
    typ         VARCHAR(15) NOT NULL, 
    CONSTRAINT uzytkownik_pk PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS zamowienie (
    id      		INT NOT NULL,
    koszt              INT NOT NULL,
    CONSTRAINT zamowienie_pk PRIMARY KEY (id)
);

-- foreign keys constraints
ALTER TABLE administrator
    ADD CONSTRAINT administrator_uzytkownik_fk FOREIGN KEY ( id )
        REFERENCES uzytkownik ( id );

ALTER TABLE budynek
    ADD CONSTRAINT budynek_miasto_fk FOREIGN KEY ( miasto_id )
        REFERENCES miasto ( id );

ALTER TABLE dane_kontaktowe
    ADD CONSTRAINT dane_firma_fk FOREIGN KEY ( firma_cateringowa_id )
        REFERENCES firma_cateringowa ( id );

ALTER TABLE dane_kontaktowe
    ADD CONSTRAINT dane_typ_fk FOREIGN KEY ( typ_kontaktu_typ )
        REFERENCES typ_kontaktu ( typ );

ALTER TABLE dane_kontaktowe
    ADD CONSTRAINT dane_uzytkownik_fk FOREIGN KEY ( uzytkownik_id )
        REFERENCES uzytkownik ( id );

ALTER TABLE dostepnosc_atrybutu
    ADD CONSTRAINT dostepnosc_atrybut_fk FOREIGN KEY ( dodatkowy_atrybut_id )
        REFERENCES dodatkowy_atrybut ( id );

ALTER TABLE dostepnosc_atrybutu
    ADD CONSTRAINT dostepnosc_atrybutu_sala_fk FOREIGN KEY ( sala_id )
        REFERENCES sala ( id);

ALTER TABLE dostepnosc_sprzetu
    ADD CONSTRAINT dostepnosc_sprzetu_sala_fk FOREIGN KEY ( sala_id )
        REFERENCES sala ( id );

ALTER TABLE dostepnosc_sprzetu
    ADD CONSTRAINT dostepnosc_sprzetu_sprzet_fk FOREIGN KEY ( sprzet_id )
        REFERENCES sprzet ( id );

ALTER TABLE kierownik
    ADD CONSTRAINT kierownik_uzytkownik_fk FOREIGN KEY ( id )
        REFERENCES uzytkownik ( id );

ALTER TABLE komorka_organizacyjna
    ADD CONSTRAINT komorka_kierownik_fk FOREIGN KEY ( kierownik_id )
        REFERENCES kierownik ( id );

ALTER TABLE pozycja
    ADD CONSTRAINT pozycja_produkt_spozywczy_fk FOREIGN KEY ( produkt_spozywczy_id )
        REFERENCES produkt_spozywczy ( id );

ALTER TABLE pozycja
    ADD CONSTRAINT pozycja_zamowienie_fk FOREIGN KEY ( zamowienie_id )
        REFERENCES zamowienie ( id );

ALTER TABLE pracownik
    ADD CONSTRAINT pracownik_komorka_fk FOREIGN KEY ( komorka_organizacyjna_id )
        REFERENCES komorka_organizacyjna ( id );

ALTER TABLE pracownik
    ADD CONSTRAINT pracownik_uzytkownik_fk FOREIGN KEY ( id )
        REFERENCES uzytkownik ( id );

ALTER TABLE produkt_spozywczy
    ADD CONSTRAINT produkt_firma_fk FOREIGN KEY ( firma_cateringowa_id )
        REFERENCES firma_cateringowa ( id);

ALTER TABLE projekt
    ADD CONSTRAINT projekt_komorka_fk FOREIGN KEY ( komorka_organizacyjna_id )
        REFERENCES komorka_organizacyjna ( id);

ALTER TABLE przypisanie_produktu
    ADD CONSTRAINT przypisanie_klasyfikacja_fk FOREIGN KEY ( klasyfikacja_produktu_id )
        REFERENCES klasyfikacja_produktu ( id );

ALTER TABLE przypisanie_produktu
    ADD CONSTRAINT przypisanie_produkt_fk FOREIGN KEY ( produkt_spozywczy_id)
        REFERENCES produkt_spozywczy ( id);

ALTER TABLE rezerwacja_obslugi
    ADD CONSTRAINT rezerwacja_dod_obsluga_fk FOREIGN KEY ( dodatkowa_obsluga_id )
        REFERENCES dodatkowa_obsluga ( id );

ALTER TABLE rezerwacja
    ADD CONSTRAINT rezerwacja_projekt_fk FOREIGN KEY ( projekt_id)
        REFERENCES projekt ( id );

ALTER TABLE rezerwacja_obslugi
    ADD CONSTRAINT rezerwacja_rezerwacja_fk FOREIGN KEY ( rezerwacja_id )
        REFERENCES rezerwacja ( id );

ALTER TABLE rezerwacja
    ADD CONSTRAINT rezerwacja_sala_fk FOREIGN KEY ( sala_id)
        REFERENCES sala ( id );

ALTER TABLE rezerwacja
    ADD CONSTRAINT rezerwacja_zamowienie_fk FOREIGN KEY ( zamowienie_id )
        REFERENCES zamowienie ( id );

ALTER TABLE sala
    ADD CONSTRAINT sala_budynek_fk FOREIGN KEY ( budynek_id )
        REFERENCES budynek ( id );

ALTER TABLE sprzet
    ADD CONSTRAINT sprzet_rodzaj_sprzetu_fk FOREIGN KEY ( rodzaj_sprzetu_id )
        REFERENCES rodzaj_sprzetu ( id );
