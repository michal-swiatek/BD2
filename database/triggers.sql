DROP TRIGGER IF EXISTS denormalizacja_koszt_ins;

-- used to update column koszt in tables rezerwacja and zamowienie, when new pozycja is inserted
CREATE TRIGGER denormalizacja_koszt_ins AFTER INSERT ON pozycja 
FOR EACH ROW
BEGIN
	DECLARE temp INT;
	SELECT cena INTO temp FROM produkt_spozywczy p WHERE p.id = NEW.produkt_spozywczy_id;
	UPDATE zamowienie z SET z.koszt = z.koszt + temp * NEW.liczba WHERE NEW.zamowienie_id = z.id;
	UPDATE rezerwacja r SET r.koszt = r.koszt + temp * NEW.liczba WHERE r.zamowienie_id = NEW.zamowienie_id;
END //

DROP TRIGGER IF EXISTS denormalizacja_koszt_up//

-- used to update column koszt in tables rezerwacja and zamowienie, when rows in table pozycja are updated
CREATE TRIGGER denormalizacja_koszt_up BEFORE UPDATE ON pozycja
FOR EACH ROW
BEGIN
	DECLARE temp INT;
	SELECT cena INTO temp FROM produkt_spozywczy p WHERE p.id = NEW.produkt_spozywczy_id;
	UPDATE zamowienie z SET z.koszt = z.koszt + temp * (NEW.liczba - OLD.liczba) WHERE NEW.zamowienie_id = z.id;
	UPDATE rezerwacja r SET r.koszt = r.koszt + temp * (NEW.liczba - OLD.liczba) WHERE r.zamowienie_id = NEW.zamowienie_id;
END //
