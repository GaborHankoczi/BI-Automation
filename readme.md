# Bemutatás
A projekt célja egy olyan üzleti intelligencia rendszer kialakítása, ami egy cég által készített
audiovizuális műsorok nézettségét/hallgatottságát gyűjti össze, dolgozza fel, illetve
vizualizálja. Ugyan azon műsorok elérhetőek youtube és podcast rendszerekben, ezekből
származó megtekintések és meghallgatások összegzése és értelmezése a cél.
# Főbb funkciók
- Választott adatforrás(ok).
    - Google analytics 4 (Data API)
    - Youtube analytics
    - Simplecast (https://apidocs.simplecast.com/)k
- Adattárolás megvalósításának leírása:
    - Raw (az adatforrásoktól szerzett adatok tárolása csv, vagy json formában)
    - Staging (A nyers adatok először adatbázisba töltött változata)
    - Data Warehouse (Reporing célra tisztázott és felhasználható adatok)
- Megvalósítandó ETL/ELT job-ok.
    - Adatok letöltése az adatforrásokból
        ▪ Ütemezve hetente
    - Adatok adatbázisba töltése
        ▪ Az előző job után
    - Adatok tisztítása, normalizálása
        ▪ Az előző job után
    - Átalakítás és aggregálás
        ▪ Az előző job után
    - Használható adatok a Data Warehouse-ba írása
        ▪ Az előző job után
- Adatok végső helyének bemutatása.
    - Az adatok az MSSQL adatbázisban a Data Warehouseban lesznek végül elhelyezve
- Megjelenítési réteg (egyedi vagy report).
    - Legolvasottab cikkek (Heti bontásban)
    - Összes olvasottság (Heti bontásban)
    - A heti összolvasottség a korábbi heti összolvasottsághoz képest összehasonlítás
    - Epizódok megtekintettsége és hallgatottsága
# Technológiák
A megvalósítás során használt technológiák felsorolása és leírása, hogy melyiknek mi a
célja.
- MSSQL adatbázis
- SQL Server Integration Services az ETL folyamatokhoz
- Az adatforrásokból az adatok letöltéséért egy egyedi python script lesz a felelős
- PowerBI reporting célokra