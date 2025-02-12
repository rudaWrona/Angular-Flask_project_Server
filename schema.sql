CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE IF NOT EXISTS "gry"(
"BGGId" TEXT, "Name" TEXT, "Description" TEXT, "YearPublished" TEXT,
 "GameWeight" TEXT, "AvgRating" TEXT, "BayesAvgRating" TEXT, "StdDev" TEXT,
 "MinPlayers" TEXT, "MaxPlayers" TEXT, "ComAgeRec" TEXT, "LanguageEase" TEXT,
 "BestPlayers" TEXT, "GoodPlayers" TEXT, "NumOwned" TEXT, "NumWant" TEXT,
 "NumWish" TEXT, "NumWeightVotes" TEXT, "MfgPlaytime" TEXT, "ComMinPlaytime" TEXT,
 "ComMaxPlaytime" TEXT, "MfgAgeRec" TEXT, "NumUserRatings" TEXT, "NumComments" TEXT,
 "NumAlternates" TEXT, "NumExpansions" TEXT, "NumImplementations" TEXT, "IsReimplementation" TEXT,
 "Family" TEXT, "Kickstarted" TEXT, "ImagePath" TEXT, "Rank:boardgame" TEXT,
 "Rank:strategygames" TEXT, "Rank:abstracts" TEXT, "Rank:familygames" TEXT, "Rank:thematic" TEXT,
 "Rank:cgs" TEXT, "Rank:wargames" TEXT, "Rank:partygames" TEXT, "Rank:childrensgames" TEXT,
 "Cat:Thematic" TEXT, "Cat:Strategy" TEXT, "Cat:War" TEXT, "Cat:Family" TEXT,
 "Cat:CGS" TEXT, "Cat:Abstract" TEXT, "Cat:Party" TEXT, "Cat:Childrens" TEXT);
CREATE TABLE uzytkownicy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nazwa TEXT NOT NULL UNIQUE,
    haslo TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    avatarPath TEXT);
CREATE TABLE reset_hasel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uzytkownik_id INTEGER NOT NULL,
    kod TEXT NOT NULL,
    uzyty BOOLEAN DEFAULT 0,
    czas DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uzytkownik_id) REFERENCES uzytkownicy(id)
);
CREATE TABLE wydarzenia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organizator_id INTEGER NOT NULL,
    nazwa TEXT NOT NULL,
    dzien TEXT NOT NULL,
    czas TEXT NOT NULL,
    miejsce TEXT NOT NULL,
    sloty INTEGER,
    opis TEXT,
    FOREIGN KEY (organizator_id) REFERENCES uzytkownicy(id)
);
CREATE TABLE zapisy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uzytkownik_id INTEGER NOT NULL,
    wydarzenie_id INTEGER NOT NULL,
    preferowana_gra TEXT NOT NULL,
    FOREIGN KEY (uzytkownik_id) REFERENCES uzytkownicy(id),
    FOREIGN KEY (wydarzenie_id) REFERENCES wydarzenia(id)
);
CREATE TABLE ankiety (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wydarzenie_id INTEGER NOT NULL,
    gra TEXT NOT NULL,
    punkty INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (wydarzenie_id) REFERENCES wydarzenia(id)
);
CREATE INDEX "nazwa_index" on "gry" ("Name");